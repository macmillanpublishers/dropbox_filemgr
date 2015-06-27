import os
import urlparse

from dropbox.client import DropboxClient, DropboxOAuth2Flow
from flask import abort, Flask, redirect, render_template, request, session, url_for

# App key and secret from the App console (dropbox.com/developers/apps)
APP_KEY = os.environ['APP_KEY']
APP_SECRET = os.environ['APP_SECRET']

app = Flask(__name__)
app.config['DEBUG'] = os.environ['DEBUG'] == 'True'

# A random secret used by Flask to encrypt session data cookies
app.secret_key = os.environ['FLASK_SECRET_KEY']

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

    return render_template('done.html', display_name=client.account_info()['display_name'])


if __name__ == '__main__':
    app.run()
