from functools import update_wrapper

from django.contrib import admin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import RedisServer
from .views import inspect_view


class RedisServerAdmin(admin.ModelAdmin):
    class Media:
        css = {'all': ('redisboard/admin.css',)}

    list_display = (
        '__str__',
        'status',
        'memory',
        'clients',
        'details',
        'cpu_utilization',
        'slowlog',
        'tools',
    )

    list_filter = ('label',)
    ordering = ('label', 'url')

    @admin.display(description=_('Details'))
    def details(self, obj):
        return obj.details_html()

    @admin.display(description=_('CPU Utilization'))
    def cpu_utilization(self, obj):
        return obj.cpu_utilization_html()

    @admin.display(description=_('Slowlog'))
    def slowlog(self, obj):
        return obj.slowlog_html()

    @admin.display(description=_('Status'))
    def status(self, obj):
        return obj.stats['status']

    @admin.display(description=_('Memory'))
    def memory(self, obj):
        return obj.stats['memory']

    @admin.display(description=_('Clients'))
    def clients(self, obj):
        return obj.stats['clients']

    @admin.display(description=_('Tools'))
    def tools(self, obj):
        return format_html('<a href="{}">{}</a>', reverse("admin:redisboard_redisserver_inspect", args=(obj.id,)), _("Inspect"))

    def get_urls(self):
        urlpatterns = super(RedisServerAdmin, self).get_urls()
        from django.urls import path

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            return update_wrapper(wrapper, view)

        return [path('<int:server_id>/inspect/', wrap(self.inspect_view), name='redisboard_redisserver_inspect')] + urlpatterns

    def inspect_view(self, request, server_id):
        server = get_object_or_404(RedisServer, id=server_id)
        if self.has_change_permission(request, server) and request.user.has_perm('redisboard.can_inspect'):
            return inspect_view(request, server)
        else:
            return HttpResponseForbidden("You can't inspect this server.")


admin.site.register(RedisServer, RedisServerAdmin)
