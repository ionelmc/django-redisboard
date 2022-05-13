import redis

if __name__ == '__main__':
    conn = redis.StrictRedis()
    while True:
        conn.set('str-big', 'bar' * 1000)
        conn.delete('str-big')
