import re
from datetime import datetime, timedelta
import redis

from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.conf import settings

from .utils import cached_property

REDISBOARD_DETAIL_FILTERS = [re.compile(name) for name in getattr(settings, 'REDISBOARD_DETAIL_FILTERS', (
    'aof_enabled', 'bgrewriteaof_in_progress', 'bgsave_in_progress',
    'changes_since_last_save', 'db.*', 'db1', 'last_save_time',
    'multiplexing_api', 'total_commands_processed',
    'total_connections_received', 'uptime_in_days', 'uptime_in_seconds',
    'vm_enabled', 'redis_version'
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

class RedisServer(models.Model):
    class Meta:
        unique_together = ('hostname', 'port')
        verbose_name = _("Redis Server")
        verbose_name_plural = _("Redis Servers")
        permissions = (
            ("can_inspect", "Can inspect redis servers"),
        )

    hostname = models.CharField(_("Hostname"), max_length=250, help_text=_('this can also be the absolute path to a redis socket'))
    port = models.IntegerField(_("Port"), validators=[
        MaxValueValidator(65535), MinValueValidator(1)
    ], default=6379, blank=True, null=True)
    password = models.CharField(_("Password"), max_length=250,
                                null=True, blank=True)

    def clean(self):
        if not self.hostname.startswith('/') and not self.port:
            raise ValidationError(_('Please provide either a hostname AND a port or the path to a redis socket'))


    @cached_property
    def connection(self):
        if self.hostname.startswith('/'):
            unix_socket_path = self.hostname
            hostname = None
        else:
            hostname = self.hostname
            unix_socket_path = None
        return redis.Redis(
            host = hostname,
            port = self.port,
            password = self.password,
            unix_socket_path=unix_socket_path,
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
                    info.get('used_memory_peak_human', 'n/a')
                ),
                'clients': info['connected_clients'],
                'brief_details': SortedDict(
                    prettify(k, v)
                    for k, v in sorted(info.items(), key=lambda (k,v): k)
                    if any(name.match(k) for name in REDISBOARD_DETAIL_FILTERS)
                )
            }
        except redis.exceptions.ConnectionError:
            return {
                'status': 'DOWN',
                'clients': 'n/a',
                'memory': 'n/a',
                'details': {},
                'brief_details': {},
            }
        except redis.exceptions.ResponseError, e:
            return {
                'status': 'ERROR: %s' % e.args,
                'clients': 'n/a',
                'memory': 'n/a',
                'details': {},
                'brief_details': {},
            }


    def __unicode__(self):
        if self.port:
            return "%s:%s" % (self.hostname, self.port)
        return self.hostname
