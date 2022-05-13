import os

import django
import redis

if __name__ == '__main__':
    os.putenv('DJANGO_SETTINGS_MODULE', 'test_project.settings')
    django.setup()
    conn = redis.StrictRedis()
    # conn.flushall()
    # conn.select(9)
    # conn.flushdb()
    import test_redisboard

    conn.set('monotonic:str', b'\n'.join(f'item-{i}'.encode() for i in range(10000)))
    test_redisboard.make_test_data(conn, size=15000)
    conn.select(1)
    for i in range(15000):
        conn.set(i, i)

    conn.eval(
        """
        local c = 0
        while c < 1000000 do
            redis.call('get', 'str')
            c = c + 1
        end
        """,
        0,
    )
