from logging import getLogger
logger = getLogger(__name__)

from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils.datastructures import SortedDict
from django.conf import settings
from django.utils.functional import curry
from django.http import HttpResponseNotFound

from redis.exceptions import ResponseError

from .utils import LazySlicingIterable

REDISBOARD_ITEMS_PER_PAGE = getattr(settings, 'REDISBOARD_ITEMS_PER_PAGE',
    100)


def safeint(value):
    try:
        return int(value)
    except ValueError:
        return value


def _fixup_pair((a, b)):
    return a, safeint(b)

LENGTH_GETTERS = {
    'list': lambda conn, key: conn.llen(key),
    'string': lambda conn, key: conn.strlen(key),
    'set': lambda conn, key: conn.scard(key),
    'zset': lambda conn, key: conn.zcount(key, '-inf', '+inf'),
    'hash': lambda conn, key: conn.hlen(key),
}


def _get_key_info(conn, key):
    try:
        obj_type = conn.type(key) 
        pipe = conn.pipeline()
        pipe.execute_command('DEBUG', 'OBJECT', key)
        LENGTH_GETTERS[obj_type](pipe, key)
        pipe.ttl(key)
        details, obj_length, obj_ttl = pipe.execute()
        pass
        return {
            'type': obj_type,
            'name': key,
            'details': details if isinstance(details, dict) else dict(
                _fixup_pair(i.split(':')) for i in details.split() if ':' in i
            ),
            'length': obj_length,
            'ttl': obj_ttl,
        }
    except ResponseError, e:
        logger.exception("Failed to get details for key %r", key)
        return {
            'type': "n/a",
            'length': "n/a",
            'name': key,
            'details': {},
            'error': str(e),
            'ttl': "n/a",
        }

VALUE_GETTERS = {
    'list': lambda conn, key, start=0, end=-1: [(pos + start, val)
        for (pos, val) in enumerate(conn.lrange(key, start, end))],
    'string': lambda conn, key, *args: [('string', conn.get(key))],
    'set': lambda conn, key, *args: list(enumerate(conn.smembers(key))),
    'zset': lambda conn, key, start=0, end=-1: [(pos + start, val)
        for (pos, val) in enumerate(conn.zrange(key, start, end))],
    'hash': lambda conn, key, *args: conn.hgetall(key).items(),
    'n/a': lambda conn, key, *args: (),
}


def _get_key_details(conn, db, key, page):
    conn.execute_command('SELECT', db)
    details = _get_key_info(conn, key)
    details['db'] = db
    if details['type'] in ('list', 'zset'):
        details['data'] = Paginator(
            LazySlicingIterable(
                lambda: details['length'],
                curry(VALUE_GETTERS[details['type']], conn, key)
            ),
            REDISBOARD_ITEMS_PER_PAGE
        ).page(page)
    else:
        details['data'] = VALUE_GETTERS[details['type']](conn, key)

    return details


def _get_db_summary(server, db):
    server.connection.execute_command('SELECT', db)
    pipe = server.connection.pipeline()

    pipe.dbsize()
    for i in range(server.sampling_threshold):
        pipe.randomkey()

    results = pipe.execute()
    size = results.pop(0)
    keys = sorted(set(results))

    pipe = server.connection.pipeline()
    for key in keys:
        pipe.execute_command('DEBUG', 'OBJECT', key)
        pipe.ttl(key)

    total_memory = 0
    volatile_memory = 0
    persistent_memory = 0
    total_keys = 0
    volatile_keys = 0
    persistent_keys = 0
    results = pipe.execute()
    for key, details, ttl in zip(keys, results[::2], results[1::2]):
        if not isinstance(details, dict):
            details = dict(_fixup_pair(i.split(':'))
                for i in details.split() if ':' in i)

        length = details['serializedlength'] + len(key)

        if ttl:
            persistent_memory += length
            persistent_keys += 1
        else:
            volatile_memory += length
            volatile_keys += 1
        total_memory += length
        total_keys += 1

    if total_keys:
        total_memory = (total_memory / total_keys) * size
    else:
        total_memory = 0

    if persistent_keys:
        persistent_memory = (persistent_memory / persistent_keys) * size
    else:
        persistent_memory = 0

    if volatile_keys:
        volatile_memory = (volatile_memory / volatile_keys) * size
    else:
        volatile_memory = 0

    return dict(
        size=size,
        total_memory=total_memory,
        volatile_memory=volatile_memory,
        persistent_memory=persistent_memory,
    )


def _get_db_details(server, db):
    conn = server.connection
    conn.execute_command('SELECT', db)
    size = conn.dbsize()

    key_details = {}
    if size > server.sampling_threshold:
        sampling = True
        pipe = conn.pipeline()
        for _ in xrange(server.sampling_size):
            pipe.randomkey()

        for key in set(pipe.execute()):
            key_details[key] = _get_key_info(conn, key)

    else:
        sampling = False
        for key in conn.keys():
            key_details[key] = _get_key_info(conn, key)

    return dict(
        keys=key_details,
        sampling=sampling,
    )


def inspect(request, server):
    stats = server.stats
    conn = server.connection
    database_details = SortedDict()
    key_details = None

    if stats['status'] == 'UP':
        if 'key' in request.GET:
            key = request.GET['key']
            db = request.GET.get('db', 0)
            page = request.GET.get('page', 1)
            key_details = _get_key_details(conn, db, key, page)
        else:
            databases = sorted(name[2:] for name in conn.info()
                if name.startswith('db'))
            total_size = 0
            for db in databases:
                database_details[db] = summary = _get_db_summary(server, db)
                total_size += summary['size']
            if total_size < server.sampling_threshold:
                for db in databases:
                    database_details[db].update(
                        _get_db_details(server, db),
                        active=True,
                    )
            elif 'db' in request.GET:
                db = request.GET['db']
                if db in database_details:
                    database_details[db].update(
                        _get_db_details(server, db),
                        active=True,
                    )
                else:
                    return HttpResponseNotFound("Unknown database.")
    return render(request, "redisboard/inspect.html", {
        'databases': database_details,
        'key_details': key_details,
        'original': server,
        'stats': stats,
        'app_label': 'redisboard',
    })

