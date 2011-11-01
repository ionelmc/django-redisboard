import redis

from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from .utils import cached_property

class RedisServer(models.Model):
    class Meta:
        unique_together = ('hostname', 'port')
        
    hostname = models.CharField(_("Hostname"), max_length=250)
    port = models.IntegerField(_("Port"), validators=[
        MaxValueValidator(65535), MinValueValidator(1)
    ], default=6379)
    password = models.CharField(_("Password"), max_length=250,
                                null=True, blank=True)


    @cached_property
    def connection(self):
        return redis.Redis(
            host = self.hostname,
            port = self.port,
            password = self.password
        )

    @connection.deleter
    def connection(self, value):
        value.connection_pool.disconnect()

    @cached_property
    def stats(self):
        try:
            info = self.connection.info()
            return {
                'status': 'UP',
                'details': info,
                'memory': "%s (peak: %s)" % (
                    info['used_memory_human'],
                    info['used_memory_peak_human']
                ),
                'clients': info['connected_clients'],
            }
        except redis.exceptions.ConnectionError:
            return {
                'status': 'DOWN',
                'clients': 'n/a',
                'memory': 'n/a',
                'details': {},
            }

    def __unicode__(self):
        return "%s:%s" % (self.hostname, self.port)
