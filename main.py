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

#global variables
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
    return render_template('homeNoAuth.html')

@app.route('/login')
def login():
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
    currentlyPlaying_info = ['', '', '']
    #Currently playing song / NOT iterable, only one result.
    currentlyPlaying = sp.current_user_playing_track()
    if currentlyPlaying is not None:
        currentlyPlaying = sp.current_user_playing_track()
        album_cover_url = currentlyPlaying['item']['album']['images'][0]['url']
        artist_name = currentlyPlaying['item']['artists'][0]['name']
        song_name = currentlyPlaying['item']['name']
        currentlyPlaying_info = [album_cover_url, artist_name, song_name]

    #top tracks
    topTracks = sp.current_user_top_tracks(limit=10)
    topTracks_info = [(track['album']['images'][0]['url'], track['artists'][0]['name'], track['name']) for track in topTracks['items']]
    
    return render_template('home.html',
                           topTracks_info = topTracks_info, 
                           displayName = displayName, 
                           topArtists_info = topArtists_info,
                           recentlyPlayedTracks_info = recentlyPlayedTracks_info,
                           userProfilePicture = userProfilePicture,
                           userUrl = userUrl,
                           currentlyPlaying_info = currentlyPlaying_info
                           )

@app.route('/createCustomPlaylist', methods=['POST', 'GET'])
def createCustomPlaylist():
    if request.method == 'GET':     
        return render_template(
            "createCustomPlaylist.html"
        )

@app.route('/createRecentlyPlayedPlaylist', methods=['GET'])
def createRecentlyPlayedPlaylist():
    return render_template('createRecentlyPlayedPlaylist.html')

@app.route('/createRecentlyPlayedPlaylistFORM', methods=['POST'])
def createRecentlyPlayedPlaylistFORM():
    return 'YEP THIS IS SUPPOSED TO BE A FORM'

@app.route('/createTopTracksPlaylist', methods=['GET'])
def createTopTracksPlaylist():
    return render_template('createTopTracksPlaylist.html')

@app.route('/createTopTracksPlaylistFORM', methods=['POST'])
def createTopTracksPlaylistFORM():
    return 'YEP THIS IS SUPPOSED TO BE A FORM'

@app.route('/createRecommendationsPlaylist', methods=['GET'])
def createRecommendationsPlaylist():
    # recommended tracks
    topTracks = sp.current_user_top_tracks(limit=5)
    trackIDList = [track['id'] for track in topTracks['items'][:5]]
    recommendations20 = sp.recommendations(seed_tracks=trackIDList, limit=20) #RECOMMENDATIONS ARE BASED OFF OF TOP 5 TRACKS, GENERATES 20
    recommendations20IDs = [(track['id'])for track in recommendations20['tracks']]
    recommendations20_info = [(track['album']['images'][0]['url'], track['artists'][0]['name'], track['name']) for track in recommendations20['tracks']]

    recommendations50 = sp.recommendations(seed_tracks=trackIDList, limit=50) #RECOMMENDATIONS ARE BASED OFF OF TOP 5 TRACKS, GENERATES 50
    recommendations50IDs = [(track['id'])for track in recommendations50['tracks']]
    recommendations50_info = [(track['album']['images'][0]['url'], track['artists'][0]['name'], track['name']) for track in recommendations50['tracks']]

    recommendations100 = sp.recommendations(seed_tracks=trackIDList, limit=100) #RECOMMENDATIONS ARE BASED OFF OF TOP 5 TRACKS, GENERATES 100
    recommendations100IDs = [(track['id'])for track in recommendations100['tracks']]
    recommendations100_info = [(track['album']['images'][0]['url'], track['artists'][0]['name'], track['name']) for track in recommendations100['tracks']]

    return render_template('createRecommendationsPlaylist.html',
                        recommendations20_info = recommendations20_info,
                        recommendations20IDs = recommendations20IDs,
                        recommendations50_info = recommendations50_info,
                        recommendations50IDs = recommendations50IDs,
                        recommendations100_info = recommendations100_info,
                        recommendations100IDs = recommendations100IDs
                           )

#Handles Form Submission (button) for creating a RECCOMENDATIONS Playlist
@app.route('/createRecomendationsPlaylistFORM', methods=['POST'])
def createRecomendationsPlaylistFORM():
    if request.method == 'POST':
        recommendationsIDs = request.form.getlist('recommendationsIDs[]')
        user = sp.current_user()
        userID = user['id']
        playlist = sp.user_playlist_create(user=userID, name="Your Recommendation Playlist", public=False, collaborative=False, description="Playlist generated by FlowFinder")
        playlistID = playlist['id']
        # Add tracks to the playlist
        sp.user_playlist_add_tracks(user=userID, playlist_id=playlistID, tracks=recommendationsIDs)
        return redirect('/main') #maybe redirect to new playlist page?

#Page that shows genre form, upon submission we redirect to createPlaylistgenres endpoint
@app.route('/createPlaylistGenre', methods=['GET'])
def createPlaylistGenre():
    return render_template('createPlaylistGenre.html',
                            music_genres = music_genres
                           )

#Handles Form Submission for Creating a GENRE playlist.
@app.route('/createPlaylistGenreFORM', methods=['POST'])
def createPlaylistGenreFORM():
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
    
@app.route('/logout') #Clears session data, effetively logging out the user, and redirects to the home page.
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)