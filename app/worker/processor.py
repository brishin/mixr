import redis, facebook, json, requests, re

r = redis.StrictRedis(host='taleyarn.com', port=6379, db=0)
SPOTIFY_API = 'http://ws.spotify.com/lookup/1/.json'

def worker_daemon():
  while True:
    response = r.blpop(('processUser', 'processFriend'), 0)
    if response[0] == 'processUser':
      user_id = response[1]
      try:
        get_for_user(user_id)
      except facebook.GraphAPIError:
        pass
      summerize(user_id)
    elif response[0] == 'processFriend':
      user_id = '632360934'
      friend_id = response[1]
      get_for_friend(user_id, friend_id)

def get_for_user(user_id):
  auth_key = r.hget(user_id, 'authKey')
  if not auth_key:
    print 'No auth key.'
    return
  graph = facebook.GraphAPI(auth_key)
  offset = 0
  while True:
    songs = graph.get_connections("me", "music.listens", limit=100, offset=offset)
    if 'data' in songs and len(songs['data']) == 0:
      break
    offset += 101
    process_songs(songs, user_id)

def get_for_friend(user_id, friend_id):
  auth_key = r.hget(user_id, 'authKey')
  if not auth_key:
    print 'No auth key.'
    return
  graph = facebook.GraphAPI(auth_key)
  offset = 0
  while True:
    songs = graph.get_connections(str(friend_id), "music.listens", limit=100, offset=offset)
    if 'data' in songs and len(songs['data']) == 0:
      break
    offset += 101
    process_songs(songs, friend_id)

def summerize(user_id):
  pass

def add_event():
  user_id = '632360934'
  print('qing all users')
  auth_key = r.hget(user_id, 'authKey')
  graph = facebook.GraphAPI(auth_key)
  attending = graph.get_connections('100370656773845', 'attending')
  for person in attending['data']:
    r.lpush('processFriend', person['id'])
    print('adding:' + person['id'])

def process_songs(songs, user_id):
  print((len(songs['data']), user_id))
  for song in songs['data']:
    if song['application']['name'] != u'Spotify':
      print('non spotify')
      continue
    print(song['data'])
    title = song['data']['song']['title']
    song_id = re.search(r'[\d\w]{22}$', song['data']['song']['url'])
    if song_id is None:
      print('no song id')
      continue
    song_id = song_id.group(0)

    params = {}
    params['uri'] = 'spotify:track:' + song_id
    req = requests.get(SPOTIFY_API, params=params)
    try:
      data = json.loads(req.content)
    except ValueError:
      continue
    album = data['track']['album']['name']
    if 'artists' in data['track'] and len(data['track']['artists']) > 0:
      artist = data['track']['artists'][0]['name']
    else:
      artist = None

    print((title, album, artist))

    r.hset(str(song_id), 'title', title)
    r.hset(str(song_id), 'album', album)
    r.hset(str(song_id), 'artist', artist)
    r.zincrby(str(user_id) + '_artists', artist, 1)
    r.incr(str(user_id) + '_power')
    #r.zincrby('100370656773845_a', artist, 1)


if __name__ == '__main__':
  worker_daemon()