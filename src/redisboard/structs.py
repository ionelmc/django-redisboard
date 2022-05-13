from datetime import datetime
from datetime import timedelta
from typing import Dict
from typing import NamedTuple
from typing import Union

from attr import define
from attr import field
from attr.converters import optional


def timedelta_fromseconds(sec):
    return timedelta(seconds=sec)


def int_if_positive(val):
    val = int(val)
    if val >= 0:
        return val


def dash_if_none(val):
    if val is None:
        return '-'
    else:
        return val


def ascii_if_not_none(val):
    if val is not None:
        return val.decode()


def timedelta_fromseconds_if_positive(sec):
    if sec >= 0:
        return timedelta(seconds=sec)


def datetime_fromtimestamp_usec(time_usec):
    return datetime.fromtimestamp(time_usec / 1000_000_000)


@define
class KeyInfo:
    name: str = field()
    type: str = field()
    encoding: str = field()
    ttl: timedelta = field(converter=timedelta_fromseconds_if_positive)
    length: int = field(converter=int_if_positive)
    frequency: Union[int, None] = field(converter=optional(int), default=None)
    idletime: Union[timedelta, None] = field(converter=optional(timedelta_fromseconds), default=None)


class ScanResult(NamedTuple):
    cursor: int  # next cursor
    count: int
    total: int
    data: object


@define
class DBInfo:
    id: int
    stats: Dict[str, Union[str, int]]
    cursor: int = None  # current cursor
    scan: Union[bool, ScanResult] = False
