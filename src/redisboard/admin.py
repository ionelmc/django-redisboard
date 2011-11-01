from django.contrib import admin
from .models import RedisServer

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
            "<tr><td>%s</td><td>%s</td></tr>" % i
                for i in sorted(obj.stats['details'].items(), key=lambda (k,v): k)
        )

    details.allow_tags = True

admin.site.register(RedisServer, RedisServerAdmin)
