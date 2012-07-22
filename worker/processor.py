import redis
import facebook
import json

r = redis.StrictRedis(host='taleyarn.com', port=6379, db=0)

def worker_daemon():
  while True:
    msg = json.loads(r.blpop('queue', 0))
    print msg

if __name__ == '__main__':
  worker_daemon()