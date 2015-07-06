import os
import urlparse
import redis
import json

from dropbox.client import DropboxClient, DropboxOAuth2Flow
from flask import abort, Flask, redirect, render_template, request, session, url_for

# App key and secret from the App console (dropbox.com/developers/apps)
APP_KEY = 'ac6gg5ixxf23stg'
APP_SECRET = 'ck8zgw5hreorljp'

app = Flask(__name__)
app.config['DEBUG'] = True

# A random secret used by Flask to encrypt session data cookies
app.secret_key = 'gibberishtktktk'

redis_client = redis.from_url('localhost:6379')

def get_url(route):
    '''Generate a proper URL, forcing HTTPS if not running locally'''
    host = urlparse.urlparse(request.url).hostname
    url = url_for(route,
                  _external=True,
                  _scheme='http' if host in ('127.0.0.1', 'localhost') else
                  'https')
    return url


def get_flow():
    return DropboxOAuth2Flow(APP_KEY, APP_SECRET, get_url('oauth_callback'),
                             session, 'dropbox-csrf-token')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    return redirect(get_flow().start())


@app.route('/oauth_callback')
def oauth_callback():
    '''Callback function for when the user returns from OAuth.'''
    access_token, uid, extras = get_flow().finish(request.args)
    client = DropboxClient(access_token)
    redis_client.hset('tokens', uid, access_token)

    return render_template('done.html', display_name=uid)


@app.route('/newfolder/<uid>')
def newfolder(uid):
    #278097779
    access_token = redis_client.hget('tokens', uid)
    client = DropboxClient(access_token)
    all_data = client.metadata('/')
    contents = all_data['contents']
    folders = []
    for item in all_data['contents']:
      for key in item:
        if key == 'is_dir':
          if item[key] == True:
            for path, value in item.iteritems():
              if path == 'path':
                folders.append(value)
    display_folders = "<br />".join(str(folder) for folder in folders)
    return render_template('newfolder.html', display_folders=display_folders, uid=uid)


# @app.route('/newfolder/<uid>')
# def newfolder(uid):
#     #278097779
#     access_token = redis_client.hget('tokens', uid)
#     client = DropboxClient(access_token)
#     return render_template('newfolder.html', uid=uid)


@app.route('/newfolder/createnewfolder/<uid>')
def createnewfolder(uid):
    access_token = redis_client.hget('tokens', uid)
    client = DropboxClient(access_token)
    newfolder = client.file_create_folder('APITestFolder2')
    return str(newfolder)


if __name__ == '__main__':
    app.run(debug=True)

#How do I return my string of folder names AND an html template? > jinja, use FOR loop in the templting engine; flask tutorial
#How do I pass in the UID without calling it in the url every time? > store uid in session
#How do I POST the folder creation?