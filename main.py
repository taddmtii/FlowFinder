from flask import Flask, redirect, request, session, url_for, render_template
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
import os
from dotenv import load_dotenv
from collections import Counter

load_dotenv() #load environment variables

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)

client_id = os.getenv("client_id") #get environment variable client_id
client_secret = os.getenv("client_secret") #get enrionment variable client_secret
redirect_uri = "http://localhost:5000/callback" #redirect url
scope = "playlist-read-private, playlist-read-collaborative, user-top-read, user-read-recently-played \
         playlist-modify-private, playlist-modify-public, user-library-modify, user-library-read \
         streaming, user-read-currently-playing, user-read-playback-state" #gets back users private playlists, we will need more than one scope

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

music_genres = {
    "Rock and its subgenres": [
        "alt-rock", "grunge", "indie", "punk", "punk-rock", 
        "rock", "rock-n-roll", "metal", "heavy-metal", "metal-misc", "metalcore"
    ],
    "Electronic": [
        "ambient", "breakbeat", "chicago-house", "deep-house", "detroit-techno", 
        "disco", "dub", "dubstep", "edm", "electro", "electronic", "house", 
        "minimal-techno", "techno", "trance"
    ],
    "Pop and its variants": [
        "pop", "pop-film", "power-pop", "synth-pop"
    ],
    "Hip Hop and Rap": [
        "hip-hop"
    ],
    "Folk and Traditional": [
        "acoustic", "folk", "singer-songwriter", "bluegrass", "country", "honky-tonk"
    ],
    "World Music": [
        "afrobeat", "bossanova", "brazil", "forro", "mpb", "samba", 
        "sertanejo", "latin", "latinom", "mandopop", "reggae", "reggaeton", 
        "salsa", "tango", "turkish", "world-music"
    ],
    "Classical and Opera": [
        "classical", "opera"
    ],
    "Jazz and Blues": [
        "jazz", "blues"
    ],
    "R&B and Soul": [
        "r-n-b", "soul"
    ],
    "Miscellaneous": [
        "anime", "children", "comedy", "holidays", "movies", "new-age", 
        "new-release", "show-tunes"
    ],
    "Moods and Themes": [
        "chill", "happy", "rainy-day", "romance", "sad", "sleep", "study", "summer", 
        "work-out"
    ],
    "Cultural and Language-Specific": [
        "british", "french", "german", "iranian", "malay", "spanish", "swedish"
    ],
    "Experimental and Niche": [
        "experimental", "goth", "grindcore", "industrial", "psych-rock", 
        "post-dubstep", "trip-hop"
    ],
    "Miscellaneous Genres": [
        "breakbeat", "cantopop", "comedy", "gospel", "happy", "party", "road-trip", 
        "show-tunes", "workout"
    ]
}


#Endpoints

@app.route('/') #Redirects users to the authentication page if they are not logged in, and if they are it redirects to the getplaylists page.
def home():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()): #if not logged in (checks if we have valid user token through cache handler)
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    return redirect(url_for('main'))


@app.route('/callback') #Handles the callback from the spotify authentication process. Retrives acces token and redirects to main endpoint.
def callback():
    sp_oauth.get_access_token(request.args['code'])
    return redirect(url_for('main'))

@app.route('/main') #Retrieves the users playlists from Spotify API.
def main():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()): #if not logged in (checks if we have valid user token through cache handler)
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    
    #get top artists and their genres
    topArtists = sp.current_user_top_artists(limit=5)
    topArtists_info = [(artist['images'][0]['url'], artist['name']) for artist in topArtists['items']]

    #get current users name for display
    user = sp.current_user()
    displayName = user['display_name']
    userID = user['id']
    userProfilePicture = user['images'][1]['url']
    userUrl = user['external_urls']['spotify']

    #Recently Played songs
    recentlyPlayedTracks = sp.current_user_recently_played(limit=10)
    recentlyPlayedTracks_info = [(track['track']['album']['images'][0]['url'], track['track']['album']['artists'][0]['name'], track['track']['name']) for track in recentlyPlayedTracks['items']]


    #top tracks
    topTracks = sp.current_user_top_tracks(limit=10)
    topTracks_info = [(track['album']['images'][0]['url'], track['artists'][0]['name'], track['name']) for track in topTracks['items']]

    # # recommended tracks
    topTracks = sp.current_user_top_tracks(limit=5)
    trackIDList = [track['id'] for track in topTracks['items'][:5]]
    recommendations = sp.recommendations(seed_tracks=trackIDList, limit=20) #RECOMMENDATIONS ARE BASED OFF OF TOP 5 TRACKS, GENERATES 20
    recommendationsIDs = [(track['id'])for track in recommendations['tracks']]
    recommendations_info = [(track['artists'][0]['name'], track['name']) for track in recommendations['tracks']]
    
    return render_template('home.html',
                           topTracks_info = topTracks_info, 
                           displayName = displayName, 
                           topArtists_info = topArtists_info,
                           recentlyPlayedTracks_info = recentlyPlayedTracks_info,
                           recommendations_info = recommendations_info,
                           recommendationsIDs = recommendationsIDs,
                           userProfilePicture = userProfilePicture,
                           userUrl = userUrl
                           )

@app.route('/createCustomPlaylist', methods=['POST'])
def createCustomPlaylist():
    #genre variables

    #Select Genres
    
    #Select Favorite Artists

    #Select Artists from Search
    #https://developer.spotify.com/documentation/web-api/reference/search
    
    #Select songs from songs chosen through search
    if request.method == 'POST':     
        return render_template(
            "createCustomPlaylist.html",
            music_genres = music_genres
        )

@app.route('/createPlaylistGenres', methods=['POST'])
def createPlaylistGenres():
    if request.method == 'POST':
        selected_options = request.form.getlist('Genre')
        
        recommendations = sp.recommendations(seed_genres=selected_options)
        recommendationsIDs = [(track['id'])for track in recommendations['tracks']]
        user = sp.current_user()
        userID = user['id']
        playlist = sp.user_playlist_create(user=userID, name="Genre Recommendation Playlist", public=False, collaborative=False, description="genre playlist thing")
        playlistID = playlist['id']
        # Add tracks to the playlist
        sp.user_playlist_add_tracks(user=userID, playlist_id=playlistID, tracks=recommendationsIDs)
        return redirect('/main') #maybe redirect to new playlist page?
    

@app.route('/createPlaylistRecommendations', methods=['POST'])
def createPlaylistRecommendations():
    if request.method == 'POST':
        try:
            recommendationsIDs = request.form.getlist('reccomendationIDs[]')
        except sp.SpotifyException as e:
            return render_template('Error.html')
        user = sp.current_user()
        userID = user['id']
        playlist = sp.user_playlist_create(user=userID, name="Your Recommendation Playlist", public=False, collaborative=False, description="all part of the grind")
        playlistID = playlist['id']
        # Add tracks to the playlist
        try:
            sp.user_playlist_add_tracks(user=userID, playlist_id=playlistID, tracks=recommendationsIDs)
        except sp.SpotifyException as e:
            return render_template('Error.html')
        return redirect('/main') #maybe redirect to new playlist page?

@app.route('/logout') #Clears session data, effetively logging out the user, and redirects to the home page.
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)