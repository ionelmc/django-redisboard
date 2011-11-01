from django.contrib import admin
from django.conf import settings
from .models import RedisServer

import re
from datetime import datetime, timedelta

REDISBOARD_DETAIL_FILTERS = [re.compile(name) for name in getattr(settings, 'REDISBOARD_DETAIL_FILTERS', (
    'aof_enabled', 'bgrewriteaof_in_progress', 'bgsave_in_progress',
    'changes_since_last_save', 'db.*', 'db1', 'last_save_time',
    'multiplexing_api', 'total_commands_processed',
    'total_connections_received', 'uptime_in_days', 'uptime_in_seconds',
    'vm_enabled'
))]
REDISBOARD_DETAIL_TIMESTAMP_KEYS = getattr(settings, 'REDISBOARD_DETAIL_TIMESTAMP_KEYS', (
    'last_save_time',
))
REDISBOARD_DETAIL_SECONDS_KEYS = getattr(settings, 'REDISBOARD_DETAIL_SECONDS_KEYS', (
    'uptime_in_seconds',
))


def prettify(key, value):
    if key in REDISBOARD_DETAIL_SECONDS_KEYS:
        return key, timedelta(seconds=value)
    elif key in REDISBOARD_DETAIL_TIMESTAMP_KEYS:
        return key, datetime.fromtimestamp(value)
    else:
        return key, value

class RedisServerAdmin(admin.ModelAdmin):
    list_display = (
        '__unicode__', 'status', 'memory', 'clients', 'details'
    )
    def status(self, obj):
        return obj.stats['status']

    def memory(self, obj):
        return obj.stats['memory']

    def clients(self, obj):
        return obj.stats['clients']

    def details(self, obj):
        return "<table>%s</table>" % ''.join(
            "<tr><td>%s</td><td>%s</td></tr>" % prettify(k, v)
                for k, v in sorted(obj.stats['details'].items(), key=lambda (k,v): k)
                if any(name.match(k) for name in REDISBOARD_DETAIL_FILTERS)
        )

    details.allow_tags = True

admin.site.register(RedisServer, RedisServerAdmin)
