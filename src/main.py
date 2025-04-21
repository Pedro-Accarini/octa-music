try:
    from . import __version__
except ImportError:
    from __init__ import __version__

from flask import Flask, request, render_template
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')

auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

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
                'image_url': a['images'][0]['url'] if a['images'] else None,
            }
    return render_template("spotify.html", artist=artist)

if __name__ == "__main__":
    app.run(debug=True)
