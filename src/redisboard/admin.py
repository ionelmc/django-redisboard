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
        css = {
            'all': ('redisboard/admin.css',)
        }
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
        return '<table class="details">%s</table>' % ''.join(
            "<tr><td>%s</td><td>%s</td></tr>" % i for i in
                obj.stats['brief_details'].items()
        )
    details.allow_tags = True
    details.long_description = _("Details")

    def get_urls(self):
        urlpatterns = super(RedisServerAdmin, self).get_urls()
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
        if self.has_change_permission(request, server) and request.user.has_perm('redisboard.can_inspect'):
            return inspect(request, server)
        else:
            return HttpResponseForbidden("You can't inspect this server.")

admin.site.register(RedisServer, RedisServerAdmin)
