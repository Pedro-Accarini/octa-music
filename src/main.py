from flask import Flask, request, render_template
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)

CLIENT_ID = ''
CLIENT_SECRET = ''

auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

TOP_50_GLOBAL_PLAYLIST_ID = '37i9dQZEVXbMDoHDwVN2tF'

@app.route("/", methods=["GET", "POST"])
def home():
    artist = None
    if request.method == "POST":
        artist_name = request.form["artist_name"]
        results = sp.search(q=artist_name, type='artist', limit=1)
        if results['artists']['items']:
            a = results['artists']['items'][0]
            artist = {
                'name': a['name'],
                'followers': f"{a['followers']['total']:,}",
                'popularity': a['popularity'],
                'genres': ', '.join(a['genres']),
                'image_url': a['images'][0]['url'] if a['images'] else None,
            }
    return render_template("search_pop.html", artist=artist)

@app.route("/top5")
def top5():
    top_tracks = []
    playlist = sp.playlist_items(TOP_50_GLOBAL_PLAYLIST_ID, limit=5)
    for item in playlist['items']:
        track = item['track']
        top_tracks.append({
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
            'preview_url': track['preview_url'],
        })
    return render_template("top5.html", top_tracks=top_tracks)

if __name__ == "__main__":
    app.run(debug=True)
