from functools import partial
from logging import getLogger

from django.conf import settings
from django.core.paginator import Paginator
from redis.exceptions import ResponseError

from .utils import LazySlicingIterable
from .utils import maybe_text

logger = getLogger(__name__)

REDISBOARD_ITEMS_PER_PAGE = getattr(settings, 'REDISBOARD_ITEMS_PER_PAGE', 100)

LENGTH_GETTERS = {
    b'list': lambda conn, key: conn.llen(key),
    b'string': lambda conn, key: conn.strlen(key),
    b'set': lambda conn, key: conn.scard(key),
    b'zset': lambda conn, key: conn.zcount(key, '-inf', '+inf'),
    b'hash': lambda conn, key: conn.hlen(key),
}


def get_key_info(conn, key):
    try:
        obj_type = conn.type(key)
        length_getter = LENGTH_GETTERS.get(obj_type)
        if not length_getter:
            return {
                'type': 'none',
                'name': key,
                'length': "n/a",
                'error': "The key does not exist",
                'ttl': "n/a",
                'refcount': "n/a",
                'encoding': "n/a",
                'idletime': "n/a",
            }

        pipe = conn.pipeline()

        try:
            pipe.object('REFCOUNT', key)
            pipe.object('ENCODING', key)
            pipe.object('IDLETIME', key)
            length_getter(pipe, key)
            pipe.ttl(key)

            refcount, encoding, idletime, obj_length, obj_ttl = pipe.execute()
        except ResponseError as exc:
            logger.exception("Failed to get object info for key %r: %s", key, exc)
            return {
                'type': obj_type,
                'name': key,
                'length': "n/a",
                'error': str(exc),
                'ttl': "n/a",
                'refcount': "n/a",
                'encoding': "n/a",
                'idletime': "n/a",
            }
        return {
            'type': maybe_text(obj_type),
            'name': key,
            'length': obj_length,
            'ttl': obj_ttl,
            'refcount': refcount,
            'encoding': maybe_text(encoding),
            'idletime': idletime,
        }
    except ResponseError as exc:
        logger.exception("Failed to get details for key %r: %s", key, exc)
        return {
            'type': "n/a",
            'length': "n/a",
            'name': key,
            'error': str(exc),
            'ttl': "n/a",
            'refcount': "n/a",
            'encoding': "n/a",
            'idletime': "n/a",
        }


VALUE_GETTERS = {
    'list': lambda conn, key, start=0, end=-1: [(pos + start, val) for (pos, val) in enumerate(conn.lrange(key, start, end))],
    'string': lambda conn, key, *args: [('string', conn.get(key))],
    'set': lambda conn, key, *args: list(enumerate(conn.smembers(key))),
    'zset': lambda conn, key, start=0, end=-1: [(pos + start, val) for (pos, val) in enumerate(conn.zrange(key, start, end))],
    'hash': lambda conn, key, *args: conn.hgetall(key).items(),
    'n/a': lambda conn, key, *args: (),
    'none': lambda conn, key, *args: (),
}


def get_key_details(conn, db, key, page):
    conn.execute_command('SELECT', db)
    details = get_key_info(conn, key)
    details['db'] = db
    if details['type'] in ('list', 'zset'):
        details['data'] = Paginator(
            LazySlicingIterable(lambda: details['length'], partial(VALUE_GETTERS[details['type']], conn, key)), REDISBOARD_ITEMS_PER_PAGE
        ).page(page)
    else:
        details['data'] = VALUE_GETTERS[details['type']](conn, key)

    return details


def get_db_details(server, db):
    conn = server.connection
    conn.execute_command('SELECT', db)
    size = conn.dbsize()
    is_sampling = False

    if size > server.sampling_threshold:
        is_sampling = True
        pipe = conn.pipeline()
        for _ in range(server.sampling_size):  # noqa
            pipe.randomkey()
        keys = set(filter(None, pipe.execute()))
    else:
        keys = conn.keys()

    data = {key: get_key_info(conn, key) for key in keys}
    return {
        'data': data,
        'is_sampling': is_sampling,
    }
