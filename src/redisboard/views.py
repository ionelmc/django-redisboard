from logging import getLogger
logger = getLogger(__name__)

from django.shortcuts import render
from django.utils.datastructures import SortedDict
from redis.exceptions import ResponseError

def safeint(value):
    try:
        return int(value)
    except ValueError:
        return value

def _fixup_pair((a, b)):
    return a, safeint(b)

def _get_key_details(conn, db):
    conn.execute_command('SELECT', db)
    keys = conn.keys()
    key_details = {}
    for key in keys:
        try:
            details = conn.execute_command('DEBUG', 'OBJECT', key)
            key_details[key] = {
                'type': conn.type(key),
                'details': dict(
                    _fixup_pair(i.split(':')) for i in details.split() if ':' in i
                ),
                'ttl': conn.ttl(key),
            }
        except ResponseError, e:
            logger.exception("Failed to get details for key %r", key)
            key_details[key] = {
                'type': "n/a",
                'details': {},
                'error': e,
                'ttl': "n/a",
            }
    return key_details


def inspect(request, server):
    stats = server.stats
    if stats['status'] == 'UP':
        conn = server.connection
        databases = sorted(name[2:] for name in conn.info() if name.startswith('db'))
        database_details = SortedDict()
        for db in databases:
            database_details[db] = _get_key_details(conn, db)
    else:
        database_details = {}

    return render(request, "redisboard/inspect.html", {
        'databases': database_details,
        'original': server,
        'stats': stats,
        'app_label': 'redisboard',
    })
