from django.shortcuts import render
from django.utils.datastructures import SortedDict

def _get_key_details(conn, db):
    conn.execute_command('SELECT', db)
    keys = conn.keys()
    key_details = {}
    for key in keys:
        details = conn.execute_command('DEBUG', 'OBJECT', key)

        key_details[key] = {
            'type': conn.type(key),
            'details': dict(
                i.split(':') for i in details.split() if ':' in i
            ),
            'ttl': conn.ttl(key),
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
