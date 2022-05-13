import warnings
from logging import getLogger
from traceback import format_stack

from django.conf import settings
from redis import ConnectionPool
from redis import StrictRedis

logger = getLogger(__name__)

REDISBOARD_CONNECTION_POOL_OPTIONS = getattr(settings, 'REDISBOARD_CONNECTIONPOOL_OPTIONS', {})


class ClosableStrictRedis(StrictRedis):
    connection_pool: ConnectionPool

    def __init__(self, url, password):
        super().__init__(
            single_connection_client=True,
            connection_pool=ConnectionPool.from_url(
                url,
                password=password,
                **REDISBOARD_CONNECTION_POOL_OPTIONS,
            ),
        )
        self.created_from = ''.join(format_stack(limit=50))

    def __del__(self):
        if getattr(self, 'connection', None) is not None and settings.DEBUG:
            warnings.warn(
                f'Redis connection was closed from __del__!\n\n'
                f'Created from:\n{self.created_from}\n'
                f'Current stack:\n{"".join(format_stack(limit=25))}',
                ResourceWarning,
                source=self,
            )
        self.close()

    def __exit__(self, *args):
        if not hasattr(self, 'connection'):
            return

        conn = self.connection
        if conn:
            conn.disconnect()
            self.connection = None
            self.connection_pool.release(conn)
        self.connection_pool.disconnect()

    close = __exit__
