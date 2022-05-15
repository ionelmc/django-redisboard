from logging import getLogger
from typing import Union
from urllib.parse import quote
from urllib.parse import unquote_to_bytes

from django.http import HttpResponseNotFound
from django.shortcuts import render

from .data import REDISBOARD_SCAN_COUNT
from .models import RedisServer
from .structs import DBInfo

logger = getLogger(__name__)


def inspect_key(request, server: RedisServer, db: int, key: str, cursor: int = 0, count: int = 0):
    key: bytes = unquote_to_bytes(key)
    display = server.display
    if not server.connection.exists(key):
        return HttpResponseNotFound('Key is gone.')
    stats = display.keys(db, [key])
    scan = display.value(db, key, cursor=cursor, count=count)
    return render(
        request,
        'redisboard/inspect_key.html',
        {
            'key': display.decoder.key(key),
            'encoded_key': quote(key),
            'stats': stats,
            'count': scan.count + count,
            'scan': scan,
            'db': {
                'id': db,
                'cursor': cursor,
            },
            'original': server,
            'site_header': None,
            'opts': {'app_label': 'redisboard', 'object_name': 'redisserver'},
            'media': '',
        },
    )


def inspect(request, server: RedisServer, db: Union[int, None] = None, cursor: Union[int, None] = 0):
    stats = server.stats
    active = None
    databases = []
    if stats:
        total_keys = sum(details.get('keys', 0) for details in stats.databases.values())
        if db is not None:
            if db in stats.databases:
                active = DBInfo(db, stats.databases[db], scan=True)
            else:
                active = DBInfo(db, {'keys': 0}, scan=True)
            databases = [active]
        elif total_keys < REDISBOARD_SCAN_COUNT:
            databases = [DBInfo(*item, scan=True) for item in stats.databases.items()]
        else:
            databases = [DBInfo(*item) for item in stats.databases.items()]

        for dbinfo in databases:
            if dbinfo.scan:
                dbinfo.scan = server.display.scan(dbinfo.id, cursor=cursor, **request.GET.dict())
                dbinfo.cursor = cursor
    return render(
        request,
        'redisboard/inspect.html',
        {
            'databases': databases,
            'display': server.display,
            'original': server,
            'stats': stats,
            'active': active,
            'filters': f'?{request.GET.urlencode()}' if request.GET else '',
            'site_header': None,
            'opts': {'app_label': 'redisboard', 'object_name': 'redisserver'},
            'media': '',
        },
    )
