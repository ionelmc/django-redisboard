from logging import getLogger

from django.http import HttpResponseNotFound
from django.shortcuts import render

from .models import RedisServer
from .query import get_db_details
from .query import get_key_details

logger = getLogger(__name__)


def inspect_view(request, server: RedisServer):
    stats = server.stats
    conn = server.connection
    key_details = None
    database_details = None

    if stats['status'] == 'UP':
        if 'key' in request.GET:
            key = request.GET['key']
            db = request.GET.get('db', 0)
            page = request.GET.get('page', 1)
            key_details = get_key_details(conn, db, key, page)
        else:
            database_details = {name[2:]: data for name, data in conn.info().items() if name.startswith('db')}
            total_keys = 0
            for db, details in database_details.items():
                total_keys += details['keys']
            if total_keys < server.sampling_threshold:
                for db, details in database_details.items():
                    details.update(
                        get_db_details(server, db),
                        active=True,
                    )
            elif 'db' in request.GET:
                db = request.GET['db']
                if db in database_details:
                    database_details[db].update(
                        get_db_details(server, db),
                        active=True,
                    )
                else:
                    return HttpResponseNotFound("Unknown database.")

    return render(
        request,
        "redisboard/inspect.html",
        {
            'databases': database_details,
            'key_details': key_details,
            'original': server,
            'stats': stats,
            'app_label': 'redisboard',
        },
    )
