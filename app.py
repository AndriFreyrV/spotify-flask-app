from flask import Flask, render_template, url_for, redirect, request, session, jsonify
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import base64
import requests

# TODO: ERROR HANDLING

app = Flask(__name__)
app.secret_key = 'KEY'
app.config['SESSSION_COOKIE_NAME'] = 'COOKIE'

client_id = 'YOUR CLIENT ID'
client_secret = 'YOUR CLIENT SECRET'

def make_url(base_url,params):
    out_url = base_url
    i = 0
    for key, val in params.items():
        if i == 0:
            out_url += f'?{key}={val}'
        else:
            out_url += f'&{key}={val}'
        i += 1
    return out_url


# From spotipy github repo
def _make_authorization_headers(client_id, client_secret):
    auth_header = base64.b64encode(
        f'{client_id}:{client_secret}'.encode("ascii")
    )  
    return {"Authorization": "Basic %s" % auth_header.decode("ascii")}

@app.route('/')
def index():
    base_url = 'https://accounts.spotify.com/authorize'
    params = {
        'client_id':client_id,
        'response_type':'code',
        'redirect_uri' : url_for('authorize', _external=True),
        'scope':'user-library-read+user-top-read'
    }
    auth_url = make_url(base_url,params)
    return redirect(auth_url)
    
    
@app.route('/authorize')
def authorize():
    headers = _make_authorization_headers(client_id, client_secret)
    code = str(request.args.get('code'))
    redirect_uri = url_for('authorize', _external=True)
    r = requests.post('https://accounts.spotify.com/api/token',  data = {'code': code, 'redirect_uri': redirect_uri, 'grant_type': 'authorization_code'}, headers =  headers).json()
    session["token_info"] = r
    return redirect('/topSongs')

@app.route('/topSongs')
def showTracks():
    if not session:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    username = sp.me()['display_name']
    print(username)
    top_tracks = sp.current_user_top_tracks(limit=25, offset=0, time_range='long_term')

    data_out = []
    for i in top_tracks['items']:
        data_iter = {
            'artist': i['artists'][0]['name'],
            'track_name': i['name'],
            'img_url': i['album']['images'][0]['url'],
            'snippet_url' : i['preview_url'],
            'spotify_link' : i['external_urls']['spotify']
        }
        data_out.append(data_iter)

    return render_template('index.html', data = data_out, user = username)

if __name__ == "__main__":
    app.run(debug=True)