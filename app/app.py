import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
  return app.send_static_file('index.html')

@app.route('/channel.html')
def channel():
  return app.send_static_file('channel.html')    

if __name__ == '__main__':
  # Bind to PORT if defined, otherwise default to 5000.
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port, debug=True)