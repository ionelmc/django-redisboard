import re
from datetime import datetime
from datetime import timedelta

import redis
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models

try:
    from django.utils.datastructures import SortedDict as OrderedDict
except ImportError:
    from django.utils.datastructures import OrderedDict

from django.utils.translation import ugettext_lazy as _


from .utils import cached_property
from .utils import PY3

REDISBOARD_DETAIL_FILTERS = [re.compile(name) for name in getattr(settings, 'REDISBOARD_DETAIL_FILTERS', (
    'aof_enabled', 'bgrewriteaof_in_progress', 'bgsave_in_progress',
    'changes_since_last_save', 'db.*', 'last_save_time', 'multiplexing_api',
    'total_commands_processed', 'total_connections_received', 'uptime_in_days',
    'uptime_in_seconds', 'vm_enabled', 'redis_version'
))]
REDISBOARD_DETAIL_TIMESTAMP_KEYS = getattr(settings, 'REDISBOARD_DETAIL_TIMESTAMP_KEYS', (
    'last_save_time',
))
REDISBOARD_DETAIL_SECONDS_KEYS = getattr(settings, 'REDISBOARD_DETAIL_SECONDS_KEYS', (
    'uptime_in_seconds',
))

REDISBOARD_SLOWLOG_LEN = getattr(settings, 'REDISBOARD_SLOWLOG_LEN', 10)

REDISBOARD_SOCKET_TIMEOUT = getattr(settings, 'REDISBOARD_SOCKET_TIMEOUT', None)
REDISBOARD_SOCKET_CONNECT_TIMEOUT = getattr(settings, 'REDISBOARD_SOCKET_CONNECT_TIMEOUT', None)
REDISBOARD_SOCKET_KEEPALIVE = getattr(settings, 'REDISBOARD_SOCKET_KEEPALIVE', None)
REDISBOARD_SOCKET_KEEPALIVE_OPTIONS = getattr(settings, 'REDISBOARD_SOCKET_KEEPALIVE_OPTIONS', None)


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

    label = models.CharField(
        _('Label'),
        max_length=50,
        blank=True,
        null=True,
    )

    hostname = models.CharField(
        _("Hostname"),
        max_length=250,
        help_text=_('This can also be the absolute path to a redis socket')
    )

    port = models.IntegerField(_("Port"), validators=[
        MaxValueValidator(65535), MinValueValidator(1)
    ], default=6379, blank=True, null=True)
    password = models.CharField(_("Password"), max_length=250,
                                null=True, blank=True)

    sampling_threshold = models.IntegerField(
        _("Sampling threshold"),
        default=1000,
        help_text=_("Number of keys after which only a sample (of random keys) is shown on the inspect page.")
    )
    sampling_size = models.IntegerField(
        _("Sampling size"),
        default=200,
        help_text=_("Number of random keys shown when sampling is used. Note that each key translates to a RANDOMKEY call in redis.")
    )

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
            host=hostname,
            port=self.port,
            password=self.password,
            unix_socket_path=unix_socket_path,
            socket_timeout=REDISBOARD_SOCKET_TIMEOUT,
            socket_connect_timeout=REDISBOARD_SOCKET_CONNECT_TIMEOUT,
            socket_keepalive=REDISBOARD_SOCKET_KEEPALIVE,
            socket_keepalive_options=REDISBOARD_SOCKET_KEEPALIVE_OPTIONS,
        )

    @connection.deleter
    def connection(self, value):
        value.connection_pool.disconnect()

    @cached_property
    def stats(self):
        try:
            conn = self.connection
            info = conn.info()
            slowlog = conn.slowlog_get()
            slowlog_len = conn.slowlog_len()
            return {
                'status': 'UP',
                'details': info,
                'memory': "%s (peak: %s)" % (
                    info['used_memory_human'],
                    info.get('used_memory_peak_human', 'n/a')
                ),
                'clients': info['connected_clients'],
                'brief_details': OrderedDict(
                    prettify(k, v)
                    for name in REDISBOARD_DETAIL_FILTERS
                    for k, v in (info.items() if PY3 else info.iteritems())
                    if name.match(k)
                ),
                'slowlog': slowlog,
                'slowlog_len': slowlog_len,
            }
        except redis.exceptions.ConnectionError:
            return {
                'status': 'DOWN',
                'clients': 'n/a',
                'memory': 'n/a',
                'details': {},
                'brief_details': {},
                'slowlog': [],
                'slowlog_len': 0,
            }
        except redis.exceptions.ResponseError as exc:
            return {
                'status': 'ERROR: %s' % exc.args,
                'clients': 'n/a',
                'memory': 'n/a',
                'details': {},
                'brief_details': {},
                'slowlog': [],
                'slowlog_len': 0,
            }

    def __unicode__(self):
        if self.label:
            label = '%s (%%s)' % self.label
        else:
            label = '%s'

        if self.port:
            label = label % ('%s:%s' % (self.hostname, self.port))
        else:
            label = label % self.hostname

        return label

    def slowlog_len(self):
        try:
            return self.connection.slowlog_len()
        except redis.exceptions.ConnectionError:
            return 0

    def slowlog_get(self, limit=REDISBOARD_SLOWLOG_LEN):
        try:
            for slowlog in self.connection.slowlog_get(REDISBOARD_SLOWLOG_LEN):
                yield dict(
                    id=slowlog['id'],
                    ts=datetime.fromtimestamp(slowlog['start_time']),
                    duration=slowlog['duration'],
                    command=slowlog['command'],
                )

        except redis.exceptions.ConnectionError:
            pass
