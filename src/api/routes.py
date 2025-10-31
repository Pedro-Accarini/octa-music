"""RESTful API routes for Octa Music."""
from flask import Blueprint, request, jsonify
from src.services.spotify_service import SpotifyService
from src.services.youtube_service import get_channel_stats_by_name
import os

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

spotify_service = SpotifyService()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "YOUR_API_KEY")

def create_error_response(message, status_code=400):
    """Create a standardized error response."""
    return jsonify({
        'success': False,
        'error': message,
        'data': None
    }), status_code

def create_success_response(data, message=None):
    """Create a standardized success response."""
    return jsonify({
        'success': True,
        'error': None,
        'data': data,
        'message': message
    }), 200

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return create_success_response({
        'status': 'healthy',
        'version': '1.0.0'
    })

def rate_limit_decorator():
    """Get rate limiter decorator if available."""
    try:
        from flask import current_app
        if hasattr(current_app, 'limiter'):
            return current_app.limiter.limit("20 per minute")
        return lambda f: f
    except:
        return lambda f: f

@api_bp.route('/spotify/search', methods=['POST'])
def search_spotify_artist():
    """Search for a Spotify artist by name.
    
    Expected JSON body:
    {
        "artist_name": "Artist Name"
    }
    """
    if not request.is_json:
        return create_error_response('Content-Type must be application/json', 400)
    
    data = request.get_json()
    artist_name = data.get('artist_name', '').strip()
    
    if not artist_name:
        return create_error_response('artist_name is required', 400)
    
    if len(artist_name) > 100:
        return create_error_response('artist_name must be less than 100 characters', 400)
    
    try:
        artist = spotify_service.search_artist(artist_name)
        
        if artist:
            return create_success_response(artist, 'Artist found successfully')
        else:
            return create_error_response('Artist not found', 404)
    
    except Exception as e:
        return create_error_response(f'Error searching artist: {str(e)}', 500)

@api_bp.route('/youtube/search', methods=['POST'])
def search_youtube_channel():
    """Search for a YouTube channel by name.
    
    Expected JSON body:
    {
        "channel_name": "Channel Name"
    }
    """
    if not request.is_json:
        return create_error_response('Content-Type must be application/json', 400)
    
    data = request.get_json()
    channel_name = data.get('channel_name', '').strip()
    
    if not channel_name:
        return create_error_response('channel_name is required', 400)
    
    if len(channel_name) > 100:
        return create_error_response('channel_name must be less than 100 characters', 400)
    
    try:
        yt_stats = get_channel_stats_by_name(channel_name, YOUTUBE_API_KEY)
        
        if yt_stats:
            return create_success_response(yt_stats, 'Channel found successfully')
        else:
            return create_error_response('Channel not found', 404)
    
    except Exception as e:
        return create_error_response(f'Error searching channel: {str(e)}', 500)
