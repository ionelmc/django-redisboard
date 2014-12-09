from __future__ import print_function

import pytest
import unittest
import os
import sys
import time
import logging
import tempfile
from collections import defaultdict

from process_tests import TestProcess
from redis import StrictRedis
from redisboard.models import RedisServer


@pytest.yield_fixture(scope="module")
def redis_server(db):
    socket_path = tempfile.mktemp('.sock')
    try:
        with TestProcess('redis-server', '--port', '0', '--unixsocket', socket_path) as process:
            server = RedisServer.objects.create(
                hostname=socket_path,
            )
            yield server
    finally:
        try:
            os.unlink(socket_path)
        except Exception:
            pass


@pytest.mark.django_db
def test_changelist(client, redis_server, admin_user):
    pass
