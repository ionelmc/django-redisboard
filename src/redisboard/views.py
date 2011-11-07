from logging import getLogger
logger = getLogger(__name__)

from django.shortcuts import render
from django.utils.datastructures import SortedDict
from django.conf import settings

from redis.exceptions import ResponseError

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
        details = conn.execute_command('DEBUG', 'OBJECT', key)
        obj_type = conn.type(key)
        obj_length = LENGTH_GETTERS[obj_type](conn, key)
        return {
            'type': conn.type(key),
            'name': key,
            'details': dict(
                _fixup_pair(i.split(':')) for i in details.split() if ':' in i
            ),
            'length': obj_length,
            'ttl': conn.ttl(key),
        }
    except ResponseError, e:
        logger.exception("Failed to get details for key %r", key)
        return {
            'type': "n/a",
            'length': "n/a",
            'name': key,
            'details': {},
            'error': e,
            'ttl': "n/a",
        }

VALUE_GETTERS = {
    'list': lambda conn, key, start=0, end=-1: enumerate(conn.lrange(key, start, end)),
    'string': lambda conn, key, *args: [('string', conn.get(key))],
    'set': lambda conn, key, *args: enumerate(conn.smembers(key)),
    'zset': lambda conn, key, start=0, end=-1: enumerate(conn.zrange(key, start, end)),
    'hash': lambda conn, key, *args: conn.hgetall(key).iteritems(),
}

def _get_key_details(conn, db, key):
    conn.execute_command('SELECT', db)
    details = _get_key_info(conn, key)
    details['data'] = VALUE_GETTERS[details['type']](conn, key)
    return details


def _get_db_details(conn, db):
    conn.execute_command('SELECT', db)
    keys = conn.keys()
    key_details = {}
    for key in keys:
        key_details[key] = _get_key_info(conn, key)
    return key_details


def inspect(request, server):
    stats = server.stats
    conn = server.connection
    database_details = SortedDict()
    key_details = None

    if stats['status'] == 'UP':
        if 'key' in request.GET:
            key = request.GET['key']
            db = request.GET.get('db', 0)
            key_details = _get_key_details(conn, db, key)
        else:
            databases = sorted(name[2:] for name in conn.info() if name.startswith('db'))

            for db in databases:
                database_details[db] = _get_db_details(conn, db)


    return render(request, "redisboard/inspect.html", {
        'databases': database_details,
        'key_details': key_details,
        'original': server,
        'stats': stats,
        'app_label': 'redisboard',
    })
