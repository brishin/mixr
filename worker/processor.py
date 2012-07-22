import redis
import facebook
import json

r = redis.StrictRedis(host='taleyarn.com', port=6379, db=0)

def worker_daemon():
  while True:
    response = r.blpop('processUser', 0)
    if response[0] == 'processUser':
      user_id = response[1]
      auth_key = r.hget(user_id, 'authKey')
      graph = facebook.GraphAPI(auth_key)
      offset = 0
      while True:
        songs = graph.get_connections("me", "music.listens", limit=100, offset=offset)
        if 'data' in songs and len(songs['data']) == 0:
          break
        offset += 101
        process_songs(songs)

def process_songs(songs):
  for song in songs['data']

if __name__ == '__main__':
  worker_daemon()