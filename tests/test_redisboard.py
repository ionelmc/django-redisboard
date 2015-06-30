from __future__ import print_function

import pytest
import os
import tempfile

from process_tests import TestProcess
from process_tests import wait_for_strings
from redis import StrictRedis

from redisboard.models import RedisServer

TIMEOUT = int(os.getenv('REDISBOARD_TEST_TIMEOUT', 2))


@pytest.yield_fixture(scope="module")
def redis_process():
    socket_path = tempfile.mktemp('.sock')
    try:
        with TestProcess('redis-server', '--port', '0', '--unixsocket', socket_path) as process:
            wait_for_strings(process.read, TIMEOUT, "Running")
            yield socket_path
    finally:
        try:
            os.unlink(socket_path)
        except Exception:
            pass


@pytest.yield_fixture
def redis_server(redis_process, db):
    server = RedisServer.objects.create(
        hostname=redis_process,
    )
    c = server.connection
    c.set('str', 'bar')
    c.sadd('set', 'bar')
    c.sadd('set', 'foo')
    c.hset('hash', 'key', 'val')
    c.hset('hash', 'foo', 'bar')
    c.lpush('list', 'foo', 'bar', 'foobar')
    c.zadd('sorted-set', 'foo', 1)
    c.zadd('sorted-set', 'b', 2)
    c.eval("""
        local c = 0
        while c < 1000000 do
            redis.call('get', 'str')
            c = c + 1
        end
    """, 0)
    yield server


@pytest.mark.django_db
def test_changelist(admin_client, redis_server):
    response = admin_client.get('/redisboard/redisserver/')
    print(response)
    content = response.content.decode('utf-8')
    assert '>UP</td>' in content
    assert '<dt>redis_version</dt>' in content
    assert '<a href="/redisboard/redisserver/{:d}/inspect/">Inspect</a>'.format(
        redis_server.pk) in content


@pytest.mark.django_db
def test_inspect(admin_client, redis_server):
    response = admin_client.get('/redisboard/redisserver/{:d}/inspect/'.format(redis_server.pk))
    print(response)
    content = response.content.decode('utf-8')
    assert 'Database 0:' in content
    assert '5 keys' in content
    assert '<td>UP</td>' in content
    assert '<td>redis_version</td>' in content

    assert '<a href="/redisboard/redisserver/{:d}/inspect/?key=set&db=0">set</a>'.format(
        redis_server.pk) in content
    assert '<a href="/redisboard/redisserver/{:d}/inspect/?key=str&db=0">str</a>'.format(
        redis_server.pk) in content
    assert '<a href="/redisboard/redisserver/{:d}/inspect/?key=hash&db=0">hash</a>'.format(
        redis_server.pk) in content
    assert '<a href="/redisboard/redisserver/{:d}/inspect/?key=list&db=0">list</a>'.format(
        redis_server.pk) in content
    assert '<a href="/redisboard/redisserver/{:d}/inspect/?key=sorted-set&db=0">sorted-set</a>'.format(
        redis_server.pk) in content


@pytest.mark.django_db
@pytest.mark.parametrize("key", ["set", "str", "hash", "list", "sorted-set"])
def test_key_details(admin_client, redis_server, key):
    response = admin_client.get(
        '/redisboard/redisserver/{:d}/inspect/?key={}'.format(redis_server.pk, key))
    print(response)
    content = response.content.decode('utf-8')
    assert '<h2>Key data: {}</h2>'.format(key) in content
