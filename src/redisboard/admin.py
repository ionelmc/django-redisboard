from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from functools import update_wrapper
from django.core.urlresolvers import reverse
from django.contrib import admin
from django.conf import settings
from .models import RedisServer
from .views import inspect
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
        '__unicode__', 'status', 'memory', 'clients', 'details', 'tools'
    )
    def status(self, obj):
        return obj.stats['status']
    status.long_description = _("Status")

    def memory(self, obj):
        return obj.stats['memory']
    memory.long_description = _("Memory")

    def clients(self, obj):
        return obj.stats['clients']
    clients.long_description = _("Clients")

    def tools(self, obj):
        return '<a href="%s">%s</a>' % (
            reverse("admin:redisboard_redisserver_inspect", args=(obj.id,)),
            unicode(_("Inspect"))
        )
    tools.allow_tags = True
    tools.long_description = _("Tools")

    def details(self, obj):
        return "<table>%s</table>" % ''.join(
            "<tr><td>%s</td><td>%s</td></tr>" % prettify(k, v)
                for k, v in sorted(obj.stats['details'].items(), key=lambda (k,v): k)
                if any(name.match(k) for name in REDISBOARD_DETAIL_FILTERS)
        )
    details.allow_tags = True
    details.long_description = _("Details")

    def get_urls(self):
        urlpatterns = super(RedisServerAdmin, self).get_urls()
        from django.conf.urls import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        return patterns('',
            url(r'^(\d+)/inspect/$',
                wrap(self.inspect_view),
                name='redisboard_redisserver_inspect'),
        ) + urlpatterns

    def inspect_view(self, request, server_id):
        server = get_object_or_404(RedisServer, id=server_id)
        if self.has_change_permission(request, server) and request.user.has_perm('redisboard.can_inspect'):
            return inspect(request, server)
        else:
            return HttpResponseForbidden("You can't inspect this server.")

admin.site.register(RedisServer, RedisServerAdmin)
