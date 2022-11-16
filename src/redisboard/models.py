import re
from datetime import datetime
from itertools import starmap
from logging import getLogger
from typing import TYPE_CHECKING
from typing import Dict
from typing import Type

import redis
from attr import Factory
from attr import define
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from .connection import ClosableStrictRedis
from .structs import datetime_fromtimestamp_usec
from .structs import timedelta_fromseconds
from .utils import cached_property

if TYPE_CHECKING:
    from .data import BaseDecoder
    from .data import BaseDisplay
    from .data import LengthQuery
    from .data import ValueQuery

logger = getLogger(__name__)

REDISBOARD_DECODER_CLASS: 'Type[BaseDecoder]' = import_string(
    getattr(settings, 'REDISBOARD_DECODER_CLASS', 'redisboard.data.UTF8BackslashReplaceDecoder'),
)
REDISBOARD_DISPLAY_CLASS: 'Type[BaseDisplay]' = import_string(
    getattr(settings, 'REDISBOARD_DISPLAY_CLASS', 'redisboard.data.TabularDisplay'),
)
REDISBOARD_VALUE_QUERY_CLASS: 'Type[ValueQuery]' = import_string(
    getattr(settings, 'REDISBOARD_VALUE_QUERY_CLASS', 'redisboard.data.ValueQuery'),
)
REDISBOARD_LENGTH_QUERY_CLASS: 'Type[LengthQuery]' = import_string(
    getattr(settings, 'REDISBOARD_LENGTH_QUERY_CLASS', 'redisboard.data.LengthQuery'),
)

REDISBOARD_DETAIL_FILTERS = [
    re.compile(name)
    for name in getattr(
        settings,
        'REDISBOARD_DETAIL_FILTERS',
        (
            '.*_version',
            '.*_api',
            '.*_policy',
            'redis_version',
            'redis_mode',
            'os',
        ),
    )
]
REDISBOARD_DETAIL_CONVERTERS = {
    re.compile(name): converter
    for name, converter in getattr(
        settings,
        'REDISBOARD_DETAIL_CONVERTERS',
        {
            '.*_seconds$': timedelta_fromseconds,
            'avg_ttl': timedelta_fromseconds,
            '.*_time$': datetime.fromtimestamp,
            '.*_time_usec$': datetime_fromtimestamp_usec,
        },
    ).items()
}

REDISBOARD_SLOWLOG_NUM = getattr(settings, 'REDISBOARD_SLOWLOG_NUM', 10)


def coerce_detail(key, value):
    for name, converter in REDISBOARD_DETAIL_CONVERTERS.items():
        if name.match(key):
            try:
                return key, converter(value)
            except Exception:
                logger.exception(f'Failed converting {key}={value} with {converter}')
    else:
        return key, value


def validate_url(value):
    try:
        redis.connection.parse_url(value)
    except Exception as exc:
        raise ValidationError(str(exc))


@define(slots=False)
class RedisServerStats:
    status: str = 'n/a'
    info: dict = Factory(dict)
    slowlog: list = Factory(dict)

    @cached_property
    def details(self):
        return dict(coerce_detail(k, v) for k, v in self.info.items() if any(name.match(k) for name in REDISBOARD_DETAIL_FILTERS))

    @cached_property
    def memory(self):
        if 'used_memory_human' in self.info:
            return f'{self.info["used_memory_human"]} (peak: {self.info.get("used_memory_peak_human", "n/a")})'
        else:
            return 'n/a'

    @cached_property
    def clients(self):
        return self.info.get('connected_clients', 'n/a')

    @cached_property
    def databases(self) -> Dict[int, dict]:
        return {int(name[2:]): dict(starmap(coerce_detail, data.items())) for name, data in self.info.items() if name.startswith('db')}

    def __bool__(self):
        return self.status == 'UP'


class RedisServer(models.Model):
    class Meta:
        verbose_name = _('Redis Server')
        verbose_name_plural = _('Redis Servers')
        permissions = (('can_inspect', 'Can inspect redis servers'),)

    label = models.CharField(
        verbose_name=_('Label'),
        max_length=50,
        blank=True,
        null=True,
    )
    url = models.CharField(
        verbose_name=_('URL'),
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
        verbose_name=_('Password'),
        max_length=250,
        null=True,
        blank=True,
        help_text=_('You can also specify the password here (the field is masked).'),
    )

    @cached_property
    def connection(self) -> redis.StrictRedis:
        return ClosableStrictRedis(self.url, self.password)

    @cached_property
    def display(self) -> 'BaseDisplay':
        return REDISBOARD_DISPLAY_CLASS(
            decoder_class=REDISBOARD_DECODER_CLASS,
            value_query_class=REDISBOARD_VALUE_QUERY_CLASS,
            length_query_class=REDISBOARD_LENGTH_QUERY_CLASS,
            server=self,
        )

    @cached_property
    def stats(self) -> RedisServerStats:
        try:
            conn = self.connection
            info = conn.info()
            slowlog = conn.slowlog_get(num=REDISBOARD_SLOWLOG_NUM)
            return RedisServerStats(
                status='UP',
                info=info,
                slowlog=slowlog,
            )
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as exc:
            return RedisServerStats(
                status=f'DOWN: {exc}',
            )
        except redis.exceptions.RedisError as exc:
            return RedisServerStats(
                status=f'ERROR: {exc!r}',
            )

    @cached_property
    def has_frequency(self):
        return self.stats.info['maxmemory_policy'].endswith('-lfu')

    def __str__(self):
        if self.label:
            return self.label
        else:
            return self.url
