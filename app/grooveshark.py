import re, requests, json, datetime, hashlib, random, math, urllib, time
from threading import Timer

API_BASE = 'html5.grooveshark.com'
UUID = 'FFC143A0-88CD-47F3-B22D-EDBF0F427EF3'
CLIENT = 'mobileshark'
CLIENT_REV = '20120227'
COUNTRY = {"ID":223,"CC1":0,"CC2":0,"CC3":0,"CC4":1073741824,"DMA":501,"IPR":0}
TOKEN_TTL = 120

# Salts
SALT = 'someThumbsUp'
METHOD_SALTS = {
	'getStreamKeyFromSongIDEx': 'someThumbsUp'
}

# Client overrides for different methods
METHOD_CLIENTS = {
	'getStreamKeyFromSongIDEx': 'mobileshark'
}

# Normalize urls
def normalize_attribute(string):
	return str.lower(re.subn(r'([a-z0-9][A-Z])','\1_\2',re.subn(r'([A-Z]+)([A-Z][a-z])','\1_\2',re.subn(r'/^.*::/',"",string)[0])[0])[0])

# Normalize dictionaries
def normalize(hash):
	h = {}
	for key in hash:
		attr = normalize_attribute(str(key))
		if isinstance(hash[key], dict):
			h[attr] = normalize(hash[key])
		elif isinstance(hash[key], list):
			for item in hash[key]:
				if isinstance(item, dict):
					item = normalize(item)
			h[attr] = hash[key]
		else:
			h[attr] = hash[key]
	return h

# Errors
class InvalidAuthentication(Exception):
	pass

class ReadOnlyAccess(Exception):
	pass

class GeneralError(Exception):
	pass

class ApiError(Exception):
	def __init__(self, fault):
		self.code = fault['code']
		self.message = fault['message']

	def to_s():
		return str(code) + str(message)

class Client(object):
	def __init__(self, session=None):
		self.session = session or self.get_session()
		self.get_comm_token()

	# Perform API request
	def request(self, method, params={}, secure=False):
		self.refresh_token() if self.comm_token else ''

		if method in METHOD_CLIENTS:
			agent = METHOD_CLIENTS[method]
		else:
			agent = CLIENT

		url = 'https' if secure else 'http'
		url += "://" + API_BASE + "/more.php?" + method
		body = {
			'header': {
				'session': self.session,
				'uuid': UUID,
				'client': agent,
				'clientRevision': CLIENT_REV,
				'country': COUNTRY
			},
			'method': method,
			'parameters': params
		}
		body['header']['token'] = self.create_token(method) if self.comm_token else ''
		cookies =  dict(cookies_are = "PHPSESSID=" + str(self.session))

		data = requests.post(url, 
			data=json.dumps(body), 
			headers={
				'content-type': 'text/plain',
				'accept': 'application/json'
			}, cookies=cookies)

		data = data.json
		data = normalize(data) if isinstance(data, dict) else ''

		if 'fault' in data.keys():
			raise ApiError(data['fault'])
		else:
			return data['result']

	# Obtain new session from Grooveshark
	def get_session(self):
		resp = requests.get('http://html5.grooveshark.com')
		return re.findall(r'PHPSESSID=([a-z0-9]{32});', str(resp.headers['set-cookie']))[0]

	# Get communication token
	def get_comm_token(self):
		self.comm_token = None
		self.comm_token = self.request('getCommunicationToken', {'secretKey': hashlib.md5(self.session).hexdigest()}, True)
		self.comm_token_ttl = datetime.datetime.now()

	# Sign method
	def create_token(self, method):
		rnd = ""
		for i in range(0,6):
			rnd += str(hex(int(math.floor(random.random()*16)))[2:])
		if method in METHOD_SALTS.keys():
			 salt = METHOD_SALTS[method]
		else:
			salt = SALT
		
		return rnd + hashlib.sha1(':'.join([method, self.comm_token, salt, rnd])).hexdigest()

	# Refresh communications token on ttl
	def refresh_token(self):
		get_comm_token() if (datetime.datetime.now() - self.comm_token_ttl) > datetime.timedelta(TOKEN_TTL) else ''

	# Authenticate user
	def login(self, username, password):
		data = self.request('authenticateUser', {'username': username, 'password': password}, True)
		user = User(self, data)
		raise InvalidAuthentication('Wrong username or password!')
		return user

	# Find user by ID
	def get_user_by_id(self, id):
		resp = self.request('getUserByID', {'userID': id})['user']
		if 'username' in resp:
			return User(self, resp)
		else:
			return None

	# Find user by username
	def get_user_by_username(self, name):
		resp = self.request('getUserByUsername', {'username': name})['user']
		if 'username' in resp:
			return User(self, resp)
		else:
			return None

	# Get recently active users
	def recent_users(self):
		users = []
		for user in self.request('getRecentlyActiveUsers', {})['users']:
			users.append(User(self, user))
		return users

	# Get popular songs
	# age => daily, monthly
	def popular_songs(self, age='daily'):
		if age != 'daily' or age != 'monthly':
			raise ValueError('Invalid age')
		songs = []
		for song in self.request('popularGetSongs', {'type': age})['songs']:
			songs.append(Song(song))
		return songs

	# Perform search request for query
	def search(self, category, query):
		songs = []
		results = self.request('getResultsFromSearch', {'type': category, 'query': query})['result']
		for song in results:
			songs.append(Song(song))
		return songs

	# Perform songs search request for a query
	def search_songs(self, query):
		return self.search('Songs', query)

	# Return raw response for songs search request
	def search_songs_pure(self, query):
		return self.request('getSearchResultsEx', {'type': 'Songs', 'query': query})

	# Get stream authentication by song ID
	def get_stream_auth_by_songid(self, song_id):
		convert = {'i\x01_\x02obile': 'isMobile', 'strea\x01_\x02ey': 'streamKey', 'ip': 'ip', 'strea\x01_\x02erve\x01_\x02d': 'streamServerID', 'ts': 'ts', '\x01_\x02ecs': 'uSecs', 'fil\x01_\x02oken': 'FileToken', 'fil\x01_\x02d': 'FileID'}
		temp = self.request('getStreamKeyFromSongIDEx', {
			'songID': song_id,
			'prefetch': False,
			'mobile': False,
			'country': COUNTRY
			})
		result = {}
		for item in temp:
			result[convert[item]] = temp[item]
		return result

	# Get stream authentication for song object
	def get_stream_auth(self, song):
		return self.get_stream_auth_by_songid(song.id)

	# Get song stream url by ID
	def get_song_url_by_id(self, id):
		resp = self.get_stream_auth_by_songid(id)
		return "http://" + resp['ip'] + "/stream.php?streamkey=" + resp['streamKey']

	def get_song_url(self, song):
		return self.get_song_url_by_id(song.id)

	# Set song to downloaded on grooveshark servers by id
	def set_song_download_by_id(self, id):
		stream = self.get_stream_auth_by_songid(id)
		return self.request('markSongDownloadedEx', {'streamKey': stream['streamKey'], 'streamServerID': stream['streamServerID'], 'songID': id})

	def set_song_download(self, song):
		return self.set_song_download_by_id(song.id)

	# Set the song to over 30 seconds on grooveshark servers by id
	def set_song_started_by_id(self, id):
		stream = self.get_stream_auth_by_songid(id)
		return self.request('markStreamKeyOver30Seconds', {'streamKey': stream['streamKey'], 'streamServerID': stream['streamServerID'], 'songID': id})

	def set_song_started(self, song):
		return self.set_song_download_by_id(song.id)

	# Set the song to played on grooveshark servers by id
	def set_song_played_by_id(self, id):
		stream = self.get_stream_auth_by_songid(id)
		return self.request('markSongQueueSongPlayed', {'streamKey': stream['streamKey'], 'streamServerID': stream['streamServerID'], 'songID': id, 'songQueueID': 0, 'songQueueSongID': 0})

	def set_song_played(self, song):
		return self.set_song_download_by_id(song.id)

	# Set the song to complete on grooveshark servers by id
	def set_song_complete_by_id(self, id):
		stream = self.get_stream_auth_by_songid(id)
		return self.request('markSongComplete', {'streamKey': stream['streamKey'], 'streamServerID': stream['streamServerID'], 'songID': id})

	def set_song_complete(self, song):
		return self.set_song_download_by_id(song.id)

	def set_song_events(self, song):
		Timer(30, self.set_song_started, [song]).start()
		if(int(round(float(song.duration))) != 0):
			Timer(int(round(float(song.duration))), self.set_song_complete, [song]).start()

	def testGet(self, title):
		song = self.search_songs(title)[0]
		resp = self.get_stream_auth_by_songid(song.id)
		url = 'http://' + resp['ip'] + '/stream.php?streamKey=' + resp['streamKey']
		self.set_song_download(song)
		self.set_song_played(song)
		self.set_song_events(song)
		return url

	def testRandGet(self, artist):
		songs = self.search_songs(artist)
		song = songs[int(math.floor(random.random()*len(songs)))]
		return {'title': song.name, 
		'artist': song.artist, 
		'album': song.album, 
		'artwork': song.artwork, 
		'length': song.duration}

class User(object):
	# Init user account
	def __init__(self, client, data=None):
		if dataIn:
			self.data = data
			self.id = data['user_id']
			self.username = data['username']
			self.premium = data['is_premium']
			self.email = data['email']
			self.city = data['city']
			self.country = data['country']
			self.sex = data['sex']
			self.playlists = None
			self.favorites = None
		self.client = client

	# Get user avatar URL
	def avatar():
		return "http://beta.grooveshark.com/static/user/userimages/" + id + ".jpg"

	# Get user activity for the date (COMES AS RAW RESPONSE)
	def feed(self, date=None):
		date = datetime.datetime.now() if date == None else ''
		month = date.month
		if month < 10:
			month = '0' + str(month)
		else:
			str(month)
		self.client.request('getProcessedUserFeedData', {'userID': id, 'day': str(date.year) + month + str(date.day)})

	# --------------------------------------------------------------------------
	# User Library
	# --------------------------------------------------------------------------

	# Fetch songs from library
	def library(self, page=0):
		songs = []
		resp = self.client.request('userGetSongsInLibrary', {'userID': id, 'page': str(page)})['songs']
		for song in resp:
			songs.append(Song(song))
		return songs

	# Add songs to user's library
	def library_add(self, songs=[]):
		songs = []
		for song in songs:
			toadd.append(song.to_hash())
		self.client.request('userAddSongsToLibrary', {'songs': toadd})

	# Remove song from user library
	def library_remove(self, song):
		raise ValueError('Song object required') if not isinstance(song, Song) else ''
		req = {'userID': id, 'songID': song.id, 'albumID': song.album_id, 'artistID': song.artist_id}
		self.client.request('userRemoveSongFromLibrary', req)

	def library_ts_modified(self):
		self.client.request('userGetLibraryTSModified', {'userID': id})

	# --------------------------------------------------------------------------
	# User Playlists
	# --------------------------------------------------------------------------

	# Fetch user playlists
	def playlists(self):
		return self.playlists if not self.playlists == None else ''
		results = self.client.requests('userGetPlaylists', {'userID': id})
		self.playlists = {}
		for playlist in results:
			self.playlists.append(Playlist(client, playlist, id))

	# Get playlist by ID
	def get_playlist(self, id):
		result = None
		for playlist in self.playlists:
			if playlist.id == id:
				result = playlist
		if result != None:
			result = result[0]
		return result

	# Create new user playlist
	def create_playlist(self, name, description='', songs=[]):
		toadd = []
		for song in songs:
			if isinstance(song, Song):
				toadd.append(song.id)
			else:
				toadd.append(str(song))
		self.client.request('createPlaylist',{
			'playlistName': name,
			'playlistAbout': description,
			'songIDs': toadd
			})
	# --------------------------------------------------------------------------
	# User Favorites
	# --------------------------------------------------------------------------

	# Get user favorites
	def favorites(self):
		return self.favorites if self.favorites != None else ''
		self.favorites = []
		resp = self.client.request('getFavorites', {'ofWhat': 'Songs', 'userID': id})
		for song in resp:
			self.favorites.append(Song(song))

	# Add song to favorites
	def add_favorite(self, song):
		if isinstance(song, Song):
			song_id = song.id
		else:
			song_id = song
		self.client.request('favorite', {'what': 'Song', 'ID': song_id})

	# Remove song from favorites
	def remove_favorite(self, song):
		if isinstance(song, Song):
			song_id = song.id
		else:
			song_id = song
		self.client.request('unfavorite', {'what': 'Song', 'ID': song_id}) 

class Song(object):
	def __init__(self, data=None):
		self.data = data
		self.id = data['SongID']
		self.name = data['SongName'] or data['name']
		self.artist = data['ArtistName']
		self.artist_id = data['ArtistID']
		self.album = data['AlbumName']
		self.album_id = data['AlbumID']
		self.track = data['TrackNum']
		self.duration = data['EstimateDuration']
		self.artwork = data['CoverArtFilename']
		self.playcount = data['Popularity']
		self.year = data['Year']

	# Presentable format
	def to_s(self):
		return ':'.join([self.id, self.name, self.artist])

	def to_hash(self):
		return {
			'songID': self.id,
			'songName': self.name,
			'artistName': self.artist,
			'artistID': self.artist_id,
			'albumName': self.album,
			'albumInfo': self.album_id,
			'track': self.track
		}

class Playlist(object):
	def __init__(self, client, data=None, user_id=None):
		self.client = client
		self.songs = []

		if data:
			self.id = data['playlist_id']
			self.name = data['name']
			self.about = data['about']
			self.picture = data['picture']
			self.user_id = data['user_id'] or user_id
			self.username = data['user_name']

	# Fetch playlist songs
	def load_songs(self):
		songs = self.client.request('playlistGetSongs', {'playlistID': id})['songs']
		temp = []
		for song in songs:
			temp.append(Song(song))
		self.songs = temp

	# Rename playlist
	def rename(self, name, description):
		try:
			self.client.request('renamePlaylist', {'playlistID': id, 'playlistName': name})
			self.client.request('setPlaylistAbout', {'playlistID': id, 'about': description})
			self.name = name
			self.about = description
			return True
		except:
			return False

	# Delete existing playlist
	def delete():
		self.client.request('deletePlaylist', {'playlistID': id, 'name': name})

# Test method
def getSongUrls(title):
	client = Client()
	songs = []
	if isinstance(title, dict):
		for song in title:
			songs.append(client.get_song_url(client.search_songs(song)[0]))
	else:
		songs = client.get_song_url(client.search_songs(title)[0])
	return songs

def getRandSong(artist):
	client = Client()
	response = client.testRandGet(artist)
	return {'title': response['title'], 
		'artist': response['artist'], 
		'album': response['album'], 
		'artwork': response['artwork'], 
		'length': response['length']}

def getSong(title):
	client = Client()
	response = client.testGet(title)
	return {'url': response, 'sesion': client.session}