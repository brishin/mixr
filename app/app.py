import os
from flask import Flask, abort, request, make_response, current_app
import json
from datetime import timedelta
from functools import update_wrapper
import redis
import facebook

app = Flask(__name__)
r = redis.StrictRedis(host='taleyarn.com', port=6379, db=0)

@app.route('/')
def index():
  return app.send_static_file('index.html')

@app.route('/channel.html')
def channel():
  return app.send_static_file('channel.html')

@app.route('/api/login', methods=['POST'])
def login():
  app.logger.debug(str(request.form))
  if 'authKey' in request.form and 'userID' in request.form:
    userID = request.form['userID']
    authKey = request.form['authKey']
    r.lpush('users', userID)
    r.hset(userID, 'authKey', authKey)
    graph = facebook.GraphAPI(authKey)
    pic = = graph.get_object('me/picture', type='square')
    r.hset(userID, 'pic', pic.get('url', None))
    return 'success'
  abort(400)
  
@app.route('/static/<path:file_path>')
def static_fetch(file_path):
  return app.send_static_file(str(file_path))

if __name__ == '__main__':
  # Bind to PORT if defined, otherwise default to 5000.
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port, debug=True)