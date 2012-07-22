import os, random, math
from flask import Flask, abort, request, make_response, current_app, json, Response
from datetime import timedelta
from functools import update_wrapper
import redis
import facebook
import grooveshark

app = Flask(__name__)
r = redis.StrictRedis(host='taleyarn.com', port=6379, db=0)

@app.route('/')
def index():
  return app.send_static_file('index.html')

@app.route('/channel.html')
def channel():
  return app.send_static_file('channel.html')

@app.route('/api/song', methods=['GET'])
def song():
  test = {
    'title': ["Suggestions Rock", "Distress Is The Root Of All Evil", "Heat Is Painless", "Dying Fears", "Regrets For The Fun Of It", "Ambitions In A Glass", "Signs Just Keep Getting Better", "Can't Stop The Misadventure", "Remembering Adventure", "Friendship Makes Me Sick"],
    'artist': ["Abramovic, Marina", "Agam, Yaacov", "Alajalov, Constantin", "Angelico, Fra (Giovanni da Fiesole)", "Anon", "Arbus, Diane", "Archipenko, Alexander", "Arcimboldo, Giuseppe", "Arp, Jean (Hans)", "Audubon, John James"],
    'artwork': ["http://images.grooveshark.com/static/albums/50_4685728.jpg", "http://images.grooveshark.com/static/albums/50_2393332.jpg", "http://images.grooveshark.com/static/albums/50_126423.jpg", "http://images.grooveshark.com/static/albums/50_4274427.jpg", "http://images.grooveshark.com/static/albums/50_3929125.jpg", "http://images.grooveshark.com/static/albums/50_6722700.jpg", "http://images.grooveshark.com/static/albums/50_8066301.jpg", "http://images.grooveshark.com/static/albums/50_1270594.jpg", "http://images.grooveshark.com/static/albums/50_146568.jpg", "http://images.grooveshark.com/static/albums/50_5399658.jpg"],
    'album': ["He's The DJ, I'm The Rapper", "Bigger and Deffer", "The Black Album", "Fantastic Vol. Two", "Blowout Comb", "Greatest Misses", "No One Can Do It Better", "Back For The First Time", "Things Fall Apart", "Dr. Octagon"],
    'length': ["303.000000", "263.000000", "353.000000", "245.000000", "185.000000", "234.000000", "986.000000", "234.000000", "125.000000", "923.000000"],
    'location': ["test", "test", "test", "test", "test", "test", "test", "test", "test", "test"]
  }
  random.seed()
  data = {
      'title': test['title'][int(math.floor(random.random()*10))],
      'artist': test['artist'][int(math.floor(random.random()*10))],
      'artwork': test['artwork'][int(math.floor(random.random()*10))],
      'album': test['album'][int(math.floor(random.random()*10))],
      'length': test['length'][int(math.floor(random.random()*10))],
      'location': test['location'][int(math.floor(random.random()*10))]
    }
  js = json.dumps(data)

  resp = Response(js, status=200, mimetype='application/json')
  resp.headers['Link'] = 'http://mixr.herokuapp.com'

  return resp

@app.route('/api/play', methods=['POST'])
def play():
  if request.headers['Content-Type'] == 'text/plain':
    info = grooveshark.getSong(request.data)
  elif request.headers['Content-Type'] == 'application/json':
    info = grooveshark.getSong(json.dumps(request.json)['title'])
  elif request.headers['Content-Type'] == 'application/x-www-form-urlencoded' or request.headers['Content-Type'] == 'application/x-www-form-urlencoded; charset=UTF-8':
    info = grooveshark.getSong(request.form['title'])
  else:
    print "header" + request.headers['Content-Type']
    return "415 Unsupported Media Type ;)"
  js = json.dumps(info)

  resp = Response(js, status=200, mimetype='application/json')
  resp.headers['Link'] = 'http://mixr.herokuapp.com'

  return resp

@app.route('/api/login', methods=['POST'])
def login():
  app.logger.debug(str(request.form))
  if 'authKey' in request.form and 'userID' in request.form:
    userID = request.form['userID']
    authKey = request.form['authKey']
    r.lpush('users', userID)
    r.hset(userID, 'authKey', authKey)
    # Uneeded, we can just insert the userID into the url
    # on the pag
    # graph = facebook.GraphAPI(authKey)
    # pic = graph.get_object('me/picture', type='square')
    # r.hset(userID, 'pic', pic.get('url', None))
    r.rpush('processUser', userID)
    return 'success'
  abort(400)

@app.route('/api/random', methods=['POST'])
def random():
  resp = []
  artists = get_artists()
  if request.headers['Content-Type'] == 'text/plain':
    for x in range(0, request.data):
      resp.append(grooveshark.getRandSong(artists[int(math.floor(random.random()*len(artists)))]))
  elif request.headers['Content-Type'] == 'application/json':
    for x in range(0, json.dump(request.json))['rows']:
      resp.append(grooveshark.getRandSong(artists[int(math.floor(random.random()*len(artists)))]))
  elif request.headers['Content-Type'] == 'application/x-www-form-urlencoded' or request.headers['Content-Type'] == 'application/x-www-form-urlencoded; charset=UTF-8':
    for x in range(0, request.form['rows']):
      resp.append(grooveshark.getRandSong(artists[int(math.floor(random.random()*len(artists)))]))
  else:
    print "header" + request.headers['Content-Type']
    return "415 Unsupported Media Type ;)"
  js = json.dumps(resp)

  out = Response(js, status=200, mimetype='application/json')
  out.headers['Link'] = 'http://mixr.herokuapp.com'

  return out
  
@app.route('/static/<path:file_path>')
def static_fetch(file_path):
  return app.send_static_file(str(file_path))


def get_artists():
  artists = []
  users = r.keys('*_artists')
  for user in users:
    user_info = r.zrevrangebyscore(user, '+inf', '-inf', num=25, start=0)
    for i in range(5):
      artists.append(user_info[i])
  return artists

def getSongFromAlbum(artist):
  grooveshark.getRandSong(artist)

if __name__ == '__main__':
  # Bind to PORT if defined, otherwise default to 5000.
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port, debug=True)