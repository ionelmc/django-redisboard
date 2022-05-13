import os
import re
import time
from pathlib import Path
from typing import Union

import psutil as psutil
import pytest
import requests
from process_tests import TestProcess
from process_tests import dump_on_error
from process_tests import wait_for_strings
from redis import StrictRedis
from redis.client import Pipeline

from redisboard.admin import cleanup_changelist_response
from redisboard.models import RedisServer

TIMEOUT = int(os.getenv('TEST_TIMEOUT', 60))
TEST_DATA_PATH = Path(__file__).with_name('test-data')
REALLY_LONG_STRING = 'foobar' * 1000


def make_test_data(conn: Union[StrictRedis, Pipeline], size=500):
    conn.set('my:str', 'bar')
    conn.set('my:big-str', 'foobar' * size)
    conn.set('my:bad-str', bytes(range(255)))
    conn.set('my:random-str', os.urandom(size))
    conn.set(f'bad:{REALLY_LONG_STRING}', 'big-str')
    conn.set(b'bad:' + bytes(range(255)), 'bad-str')
    conn.set(b'bad:' + os.urandom(1000), 'random-str')
    conn.sadd('my:set', 'bar')
    conn.sadd('my:set', REALLY_LONG_STRING)
    conn.sadd('my:set', bytes(range(255)))
    for i in range(size):
        conn.sadd('my:set', f'item-{i}')
    conn.sadd('my:random-set', os.urandom(1000))
    conn.hset('my:hash', 'str', 'bar')
    conn.hset('my:hash', 'big-str', REALLY_LONG_STRING)
    conn.hset('my:hash', 'bad-str', bytes(range(255)))
    for i in range(size):
        conn.hset('my:hash', f'item-{i}', 'bar')
    conn.hset('my:random-hash', 'random-str', os.urandom(1000))
    for i in range(size):
        conn.lpush('my:list', f'item-{i}')
    conn.zadd('my:zset', {f'item-{i}': i for i in range(size)})


@pytest.fixture
def redis_model(redis_server, db):
    server = RedisServer.objects.create(
        url=f'unix:///{redis_server}',
    )
    with server.connection:
        with server.connection.pipeline() as pipe:
            make_test_data(pipe)
            pipe.execute()
        server.connection.eval(
            """
            local c = 0
            while c < 1000000 do
                redis.call('get', 'str')
                c = c + 1
            end
        """,
            0,
        )
        yield server


@pytest.fixture
def empty_redis_model(redis_server, db):
    server = RedisServer.objects.create(
        url=f'unix:///{redis_server}?db=1',
    )
    with server.connection:
        yield server


@pytest.mark.django_db
def test_changelist(admin_client, redis_model):
    response = admin_client.get('/redisboard/redisserver/')
    assert cleanup_changelist_response in response._post_render_callbacks
    content = response.content.decode('utf-8')
    assert '>UP</' in content
    assert '>redis version</' in content
    assert '<a href="/redisboard/redisserver/{:d}/inspect/">Inspect</a>'.format(redis_model.pk) in content


@pytest.mark.django_db
def test_inspect(admin_client, redis_model):
    response = admin_client.get('/redisboard/redisserver/{:d}/inspect/'.format(redis_model.pk))
    content = response.content.decode('utf-8')
    assert 'Database 0:' in content
    assert '13 keys' in content
    assert '>Keys (13)</' in content
    assert '>UP</' in content
    assert '>redis version</' in content
    pk = redis_model.pk
    assert (
        f'<a href="/redisboard/redisserver/{pk}/inspect/0/key/bad%253A%2500%2501%2502%2503%2504%2505%2506%2507%2508%2509%250A%250B%250C'
        '%250D%250E%250F%2510%2511%2512%2513%2514%2515%2516%2517%2518%2519%251A%251B%251C%251D%251E%251F%2520%2521%2522%2523%2524%2525'
        '%2526%2527%2528%2529%252A%252B%252C-./0123456789%253A%253B%253C%253D%253E%253F%2540ABCDEFGHIJKLMNOPQRSTUVWXYZ%255B%255C%255D%'
        '255E_%2560abcdefghijklmnopqrstuvwxyz%257B%257C%257D~%257F%2580%2581%2582%2583%2584%2585%2586%2587%2588%2589%258A%258B%258C%25'
        '8D%258E%258F%2590%2591%2592%2593%2594%2595%2596%2597%2598%2599%259A%259B%259C%259D%259E%259F%25A0%25A1%25A2%25A3%25A4%25A5%25'
        'A6%25A7%25A8%25A9%25AA%25AB%25AC%25AD%25AE%25AF%25B0%25B1%25B2%25B3%25B4%25B5%25B6%25B7%25B8%25B9%25BA%25BB%25BC%25BD%25BE%25'
        'BF%25C0%25C1%25C2%25C3%25C4%25C5%25C6%25C7%25C8%25C9%25CA%25CB%25CC%25CD%25CE%25CF%25D0%25D1%25D2%25D3%25D4%25D5%25D6%25D7%25'
        'D8%25D9%25DA%25DB%25DC%25DD%25DE%25DF%25E0%25E1%25E2%25E3%25E4%25E5%25E6%25E7%25E8%25E9%25EA%25EB%25EC%25ED%25EE%25EF%25F0%25'
        'F1%25F2%25F3%25F4%25F5%25F6%25F7%25F8%25F9%25FA%25FB%25FC%25FD%25FE/">bad:\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r'
        '\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !&quot;#$%&amp;&#x27;()*+,-./0123456789:;&lt;=&gt;?@'
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\\x80\\x81\\x82\\x83\\x84\\x85\\x86\\x87\\x88\\x89\\x8a\\x'
        '8b\\x8c\\x8d\\x8e\\x8f\\x9…</a>' in content
    )
    assert f'<a href="/redisboard/redisserver/{pk}/inspect/0/key/my%253Ahash/">my:hash</a></td>' in content
    assert f'<a href="/redisboard/redisserver/{pk}/inspect/0/key/my%253Abig-str/">my:big-str</a></td>' in content
    assert f'<a href="/redisboard/redisserver/{pk}/inspect/0/key/my%253Arandom-str/">my:random-str</a></td>' in content
    assert f'<a href="/redisboard/redisserver/{pk}/inspect/0/key/my%253Azset/">my:zset</a></td>' in content
    assert f'<a href="/redisboard/redisserver/{pk}/inspect/0/key/my%253Aset/">my:set</a></td>' in content
    assert (
        f'<a href="/redisboard/redisserver/{pk}/inspect/0/key/bad%253A{REALLY_LONG_STRING}/">bad:{REALLY_LONG_STRING:.195}…</a>' in content
    )
    assert f'<a href="/redisboard/redisserver/{pk}/inspect/0/key/my%253Astr/">my:str</a></td>' in content
    assert f'<a href="/redisboard/redisserver/{pk}/inspect/0/key/my%253Alist/">my:list</a></td>' in content
    assert f'<a href="/redisboard/redisserver/{pk}/inspect/0/key/my%253Abad-str/">my:bad-str</a></td>' in content


@pytest.mark.django_db
def test_inspect_empty(admin_client, empty_redis_model):
    response = admin_client.get(f'/redisboard/redisserver/{empty_redis_model.pk}/inspect/')
    content = response.content.decode('utf-8')
    assert 'No database found' in content
    assert '>UP</' in content
    assert '>redis version</' in content


@pytest.mark.django_db
@pytest.mark.parametrize(
    'key',
    [
        'bad%253A%2500%2501%2502%2503%2504%2505%2506%2507%2508%2509%250A%2'
        '50B%250C%250D%250E%250F%2510%2511%2512%2513%2514%2515%2516%2517%2518%2519%251A%251B%251C%251D%251E%251F%2520%2521%2522%2523%25'
        '24%2525%2526%2527%2528%2529%252A%252B%252C-./0123456789%253A%253B%253C%253D%253E%253F%2540ABCDEFGHIJKLMNOPQRSTUVWXYZ%255B%255C'
        '%255D%255E_%2560abcdefghijklmnopqrstuvwxyz%257B%257C%257D~%257F%2580%2581%2582%2583%2584%2585%2586%2587%2588%2589%258A%258B%25'
        '8C%258D%258E%258F%2590%2591%2592%2593%2594%2595%2596%2597%2598%2599%259A%259B%259C%259D%259E%259F%25A0%25A1%25A2%25A3%25A4%25A'
        '5%25A6%25A7%25A8%25A9%25AA%25AB%25AC%25AD%25AE%25AF%25B0%25B1%25B2%25B3%25B4%25B5%25B6%25B7%25B8%25B9%25BA%25BB%25BC%25BD%25BE'
        '%25BF%25C0%25C1%25C2%25C3%25C4%25C5%25C6%25C7%25C8%25C9%25CA%25CB%25CC%25CD%25CE%25CF%25D0%25D1%25D2%25D3%25D4%25D5%25D6%25D7%'
        '25D8%25D9%25DA%25DB%25DC%25DD%25DE%25DF%25E0%25E1%25E2%25E3%25E4%25E5%25E6%25E7%25E8%25E9%25EA%25EB%25EC%25ED%25EE%25EF%25F0%2'
        '5F1%25F2%25F3%25F4%25F5%25F6%25F7%25F8%25F9%25FA%25FB%25FC%25FD%25FE',
        'my%253Ahash',
        'my%253Abig-str',
        'my%253Azset',
        'my%253Aset',
    ],
    ids='{:.16}'.format,
)
def test_key_details(admin_client, redis_model, key: str, request):
    response = admin_client.get(f'/redisboard/redisserver/{redis_model.pk}/inspect/0/key/{key}/')
    content = response.content.replace(b'\r', b'').replace(b'\n', b'')
    expected_path: Path = TEST_DATA_PATH.joinpath(f'{key.replace("%", ""):.16}.html')
    if expected_path.exists():
        expected = expected_path.read_bytes()
    else:
        expected = b'failfailfail'
    try:
        assert expected in content
    except Exception:
        if b'<fieldset class="module aligned key-data">' in content:
            content = content[content.index(b'<fieldset class="module aligned key-data">') : content.index(b'</fieldset></div>')]
        expected_path.write_bytes(content)
        raise


@pytest.mark.parametrize('entrypoint', ['redisboard', 'python -mredisboard'])
def test_cli(entrypoint, tmpdir):
    args = ['127.0.0.1:0', '--password', 'foobar', '--storage', str(tmpdir)]
    with TestProcess(*entrypoint.split() + args) as process:
        with dump_on_error(process.read):
            wait_for_strings(process.read, TIMEOUT, 'server at http://')
            t = time.time()
            port = None
            while time.time() - t < TIMEOUT and port is None:
                for conn in psutil.Process(process.proc.pid).connections('all'):
                    if conn.status == psutil.CONN_LISTEN and conn.laddr[0] == '127.0.0.1':
                        port = conn.laddr[1]
                        break
            assert port
            with requests.Session() as session:
                resp = session.get('http://127.0.0.1:%s/' % port)
                (csrftoken,) = re.findall('name=[\'"]csrfmiddlewaretoken[\'"] value=[\'"](.*?)[\'"]', resp.text)
                resp = session.post(
                    'http://127.0.0.1:%s/login/?next=/redisboard/redisserver/' % port,
                    data={
                        'csrfmiddlewaretoken': csrftoken,
                        'username': 'redisboard',
                        'password': 'foobar',
                    },
                )
                assert '<a href="/redisboard/redisserver/1/inspect/"' in resp.text
