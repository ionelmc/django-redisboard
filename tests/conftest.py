import pytest
from process_tests import TestProcess
from process_tests import wait_for_strings
from redis.client import StrictRedis


@pytest.fixture
def redis_server(tmp_path):
    redis_socket = str(tmp_path.joinpath('redis.sock'))
    with TestProcess(
        'redis-server', '--port', '0', '--save', '', '--appendonly', 'yes', '--dir', tmp_path, '--unixsocket', redis_socket
    ) as redis_server:
        wait_for_strings(redis_server.read, 2, 'ready to accept connections')
        yield redis_socket
        print(redis_server.read())


@pytest.fixture
def redis_monitor(redis_server):
    with TestProcess('redis-cli', '-s', redis_server, 'monitor') as redis_monitor:
        yield
        print(redis_monitor.read())


@pytest.fixture
def redis_conn(redis_server):
    return StrictRedis(unix_socket_path=redis_server, decode_responses=True)
