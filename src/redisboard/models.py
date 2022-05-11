import re
from datetime import datetime
from datetime import timedelta

import redis
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .utils import cached_property

REDISBOARD_DETAIL_FILTERS = [
    re.compile(name)
    for name in getattr(
        settings,
        'REDISBOARD_DETAIL_FILTERS',
        (
            'aof_enabled',
            'bgrewriteaof_in_progress',
            'bgsave_in_progress',
            'changes_since_last_save',
            'db.*',
            'last_save_time',
            'multiplexing_api',
            'total_commands_processed',
            'total_connections_received',
            'uptime_in_days',
            'uptime_in_seconds',
            'vm_enabled',
            'redis_version',
        ),
    )
]
REDISBOARD_DETAIL_TIMESTAMP_KEYS = getattr(settings, 'REDISBOARD_DETAIL_TIMESTAMP_KEYS', ('last_save_time',))
REDISBOARD_DETAIL_SECONDS_KEYS = getattr(settings, 'REDISBOARD_DETAIL_SECONDS_KEYS', ('uptime_in_seconds',))

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


def validate_url(value):
    try:
        redis.connection.parse_url(value)
    except Exception as exc:
        raise ValidationError(str(exc))


class RedisServer(models.Model):
    class Meta:
        verbose_name = _("Redis Server")
        verbose_name_plural = _("Redis Servers")
        permissions = (("can_inspect", "Can inspect redis servers"),)

    label = models.CharField(
        _('Label'),
        max_length=50,
        blank=True,
        null=True,
    )
    url = models.CharField(
        _("URL"),
        max_length=250,
        unique=True,
        help_text=_(
            '<a href="https://www.iana.org/assignments/uri-schemes/prov/redis">IANA-compliant</a> URL. Examples: <pre>'
            'redis://[[username]:[password]]@localhost:6379/0\n'
            'rediss://[[username]:[password]]@localhost:6379/0\n'
            'unix://[[username]:[password]]@/path/to/socket.sock?db=0</pre>'
        ),
        validators=[validate_url],
    )
    password = models.CharField(
        _("Password"), max_length=250, null=True, blank=True, help_text=_('You can also specify the password here (the field is masked).')
    )

    sampling_threshold = models.IntegerField(
        _("Sampling threshold"),
        default=1000,
        help_text=_("Number of keys after which only a sample (of random keys) is shown on the inspect page."),
    )
    sampling_size = models.IntegerField(
        _("Sampling size"),
        default=200,
        help_text=_("Number of random keys shown when sampling is used. Note that each key translates to a RANDOMKEY call in redis."),
    )

    @cached_property
    def connection(self) -> redis.StrictRedis:
        return redis.StrictRedis(
            single_connection_client=True,
            connection_pool=redis.ConnectionPool.from_url(
                self.url,
                password=self.password,
                retry_on_timeout=True,
            ),
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
                'memory': "%s (peak: %s)" % (info['used_memory_human'], info.get('used_memory_peak_human', 'n/a')),
                'clients': info['connected_clients'],
                'brief_details': dict(prettify(k, v) for name in REDISBOARD_DETAIL_FILTERS for k, v in info.items() if name.match(k)),
                'slowlog': slowlog,
                'slowlog_len': slowlog_len,
            }
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
            return {
                'status': 'DOWN',
                'clients': 'n/a',
                'memory': 'n/a',
                'details': {},
                'brief_details': {},
                'slowlog': [],
                'slowlog_len': 0,
            }
        except redis.exceptions.RedisError as exc:
            return {
                'status': 'ERROR: %s' % exc.args,
                'clients': 'n/a',
                'memory': 'n/a',
                'details': {},
                'brief_details': {},
                'slowlog': [],
                'slowlog_len': 0,
            }

    def slowlog_html(self):
        commands = []
        for log in self.stats['slowlog']:
            command = log['command']
            if isinstance(command, bytes):
                command = repr(command)[2:-1]

            if len(command) > 255:
                command = f'{command:252}...'

            commands.append((log['duration'], command))
        commands.sort(reverse=True)
        if commands:
            output = ''.join(f'<tr><th>{duration / 1000.0:.1f}ms</th><td>{command}</td></tr>' for duration, command in commands)
            return mark_safe(f'<table><tr><th colspan="2">Total: {self.stats["slowlog_len"]} items</th></tr>{output}</table>')

        else:
            return 'n/a'

    def details_html(self):
        output = []
        brief_details = self.stats['brief_details']
        for k, v in brief_details.items():
            k = k.replace('_', ' ')
            if isinstance(v, dict):
                keys = v.keys()
                output.append(f'<tr><td colspan="2"><table><tr><th>{k}</th>')
                output.append(''.join(f'<th>{k}</th>' for k in keys))
                output.append('</tr><tr><td></td>')
                output.append(''.join(f'<td>{v[k]}</td>' for k in keys))
                output.append('</tr></table></td></tr>')
            else:
                output.append(f'<tr><th>{k}</th><td>{v}</td></tr>')
        if output:
            return mark_safe(f'<table>{"".join(output)}</table>')
        return 'n/a'

    def cpu_utilization_html(self):
        stats = self.stats
        if stats['status'] != 'UP':
            return 'n/a'

        data = (
            'used_cpu_sys',
            'used_cpu_sys_children',
            'used_cpu_user',
            'used_cpu_user_children',
        )
        data = dict((k, stats['details'][k]) for k in data)
        total_cpu = sum(data.values())
        uptime = stats['details']['uptime_in_seconds']
        data['cpu_utilization'] = '%.3f%%' % (total_cpu / uptime if uptime else 0)

        data = sorted(data.items())

        output = []
        for k, v in data:
            k = k.replace('_', ' ')
            output.append(f'<tr><th>{k}</th><td>{v}</td></tr>')

        if output:
            return mark_safe(f'<table>{"".join(output)}</table>')
        return 'n/a'

    def __str__(self):
        if self.label:
            return f'{self.label} ({self.url})'
        else:
            return self.url
