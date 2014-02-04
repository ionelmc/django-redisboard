# vim: set fileencoding=utf-8 :
from functools import update_wrapper

from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib import admin

from .models import RedisServer
from .views import inspect

class RedisServerAdmin(admin.ModelAdmin):

    class Media:
        css = {'all': ('redisboard/admin.css', )}

    list_display = (
        '__unicode__',
        'status',
        'memory',
        'clients',
        'details',
        'cpu_utilization',
        'slowlog',
        'tools',
    )

    list_filter = 'label', 'hostname'
    ordering = ('hostname', 'port')

    def slowlog(self, obj):
        output = [(float('inf'), 'Total: %d items' % obj.slowlog_len())]
        for log in obj.slowlog_get():
            command = ' '.join(l.decode('utf-8', 'replace')
                 for l in log['command'])

            if command[100:]:
                command = command[:97] + '...'

            output.append((
                log['duration'],
                u'%.1fms: %s' % (log['duration'] / 1000., command),
            ))
        return '<br>'.join(l for _, l in sorted(output, reverse=True))
    slowlog.allow_tags = True
    slowlog.long_description = _('Slowlog')

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
        output = []
        for k, v in obj.stats['brief_details'].iteritems():
            output.append('<dt>%s</dt><dd>%s</dd>' % (k, v))

        return '<dl class="details">%s</dl>' % ''.join(output)
    details.allow_tags = True
    details.long_description = _("Details")

    def cpu_utilization(self, obj):
        stats = obj.stats
        if stats['status'] == 'DOWN':
            return ''

        data = (
            'used_cpu_sys',
            'used_cpu_sys_children',
            'used_cpu_user',
            'used_cpu_user_children',
        )
        data = dict((k, stats['details'][k]) for k in data)
        total_cpu = sum(data.itervalues())
        data['cpu_utilization'] = '%.3f%%' % (total_cpu
            / stats['details']['uptime_in_seconds'])

        data = sorted(data.items())

        output = []
        for k, v in data:
            k = k.replace('_', ' ')
            output.append('<dt>%s</dt><dd>%s</dd>' % (k, v))

        return '<dl class="details">%s</dl>' % ''.join(output)
    cpu_utilization.allow_tags = True
    cpu_utilization.long_description = _('CPU Utilization')


    def get_urls(self):
        urlpatterns = super(RedisServerAdmin, self).get_urls()
        try:
            from django.conf.urls import patterns, url
        except ImportError:
            from django.conf.urls.defaults import patterns, url
    
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
        if(self.has_change_permission(request, server)
                and request.user.has_perm('redisboard.can_inspect')):
            return inspect(request, server)
        else:
            return HttpResponseForbidden("You can't inspect this server.")

admin.site.register(RedisServer, RedisServerAdmin)

