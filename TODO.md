Potential Names:

FlowFinder
VibeCheck

Features (Goals):

- User Authentication (Spotify).
- Users can choose a genre/s, mood, potential activity, favorite artists etc...
- Make generated playlists based off of criteria.
- Recommend new songs to current playlists.
- Show users most played genre, artists and songs.
- Import playlists to spotify account.
- Ability to favorite generated playlists.
- Remove all tracks from a certain artist? (POTENTIALLY WOULD BE COOL)

Documentation Notes:

Using Authorization Code Flow for OAuth.
    Allows us to...
        1. Access User Resources
        2. Requires Secret Key
        3. Access Token Refresh
    - using this ensures that the client secret is safely stored.

Scopes: What my application has access to, what it does not (For User Safety)
    - I will need to specify the information (scopes) that I need for user permission.


Read playlists:
    -playlist-read-private (read access to users ALL (including private) playlists)
    -playlist-read-collaborative (include collaborative playlists when requesting a users playlists)
    -user-top-read (Read access to a Users top artists and tracks) *****
    -user-read-recently-played (Read access to a users recently played tracks)

Write to playlists:
    -playlist-modify-private (Write access to a users private playlists)
    -playlist-modify-public (Write access to a users public playlists)
    -user-library-modify (Write, delete access to a users "Your Music Library")
    -user-library-read (Read Access to a users library)


    -streaming (control playback of a spotify track):

#FOR CREATING PLAYLISTS:
https://developer.spotify.com/documentation/web-api/reference/create-playlist

- Create Playlist: Choose 5 genres, up to 5 of the top songs, 5 artists, OR pick an artist.
- Show Stats

HOME PAGE (main): SHOW STATS, Profile Information
CREATE: Create Playlist based off of:
    - Top 20-50 songs
    - Recommendations (Based off top 5 songs, up to 5 genres)
    - Recently Played