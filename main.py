from flask import Flask, redirect, request, session, url_for, render_template
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
import os
from dotenv import load_dotenv

load_dotenv() #load environment variables

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)

client_id = os.getenv("client_id") #get environment variable client_id
client_secret = os.getenv("client_secret") #get enrionment variable client_secret
redirect_uri = "http://localhost:5000/callback" #redirect url
scope = "playlist-read-private" #gets back users private playlists, we will need more than one scope

cache_handler = FlaskSessionCacheHandler(session) # stores token in current flask session
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True
) #this is the spotify authentiation manager

sp = Spotify(auth_manager=sp_oauth)

#Endpoints

@app.route('/') #Redirects users to the authentication page if they are not logged in, and if they are it redirects to the getplaylists page.
def home():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()): #if not logged in (checks if we have valid user token through cache handler)
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    return redirect(url_for('get_playlists'))
    # mountains = ['Everest', 'K2', 'Kilimianjaro']
    # return render_template("home.html", mountain = mountains)

@app.route('/callback') #Handles the callback from the spotify authentication process. Retrives acces token and redirects to get_playlists endpoint.
def callback():
    sp_oauth.get_access_token(request.args['code'])
    return redirect(url_for('get_playlists'))

@app.route('/get_playlists') #Retrieves the users playlists from Spotify API.
def get_playlists():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()): #if not logged in (checks if we have valid user token through cache handler)
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    
    playlists = sp.current_user_playlists() #sp is the spotify client
    playlists_info = [(pl['name'], pl['external_urls']['spotify']) for pl in playlists['items']] #iterating through every playlist
    playlists_html = '<br>'.join([f'{name}: {url}' for name, url in playlists_info])

    return playlists_html

@app.route('/logout') #Clears session data, effetively logging out the user, and redirects to the home page.
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
