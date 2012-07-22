import redis
import facebook
import json

r = redis.StrictRedis(host='taleyarn.com', port=6379, db=0)

def worker_daemon():
  while True:
    response = r.blpop('processUser', 0)
    if response[0] == 'processUser':
      user_id = response[1]

if __name__ == '__main__':
  worker_daemon()