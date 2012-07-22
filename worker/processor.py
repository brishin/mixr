import redis
import facebook
import json

r = redis.StrictRedis(host='taleyarn.com', port=6379, db=0)

def worker_daemon():
  while True:
    msg = json.loads(redis.blpop('queue', 0))
    print msg