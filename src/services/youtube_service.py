import requests
import logging
import time
from functools import wraps
from src.cache_config import CacheConfig, cache_result

logger = logging.getLogger(__name__)

# Request throttling configuration
LAST_REQUEST_TIME = {}
MIN_REQUEST_INTERVAL = 0.1  # Minimum 100ms between requests to same endpoint


def throttle_request(endpoint_key: str):
    """
    Decorator to throttle requests to external APIs.
    
    Args:
        endpoint_key: Unique key identifying the API endpoint
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            global LAST_REQUEST_TIME
            current_time = time.time()
            
            if endpoint_key in LAST_REQUEST_TIME:
                elapsed = current_time - LAST_REQUEST_TIME[endpoint_key]
                if elapsed < MIN_REQUEST_INTERVAL:
                    sleep_time = MIN_REQUEST_INTERVAL - elapsed
                    logger.debug(f"Throttling request to {endpoint_key}, sleeping {sleep_time:.3f}s")
                    time.sleep(sleep_time)
            
            LAST_REQUEST_TIME[endpoint_key] = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator


def format_number(num_str):
    """Format numbers with thousand separators."""
    try:
        num = int(num_str)
        return f"{num:,}"
    except (ValueError, TypeError):
        return num_str


@throttle_request("youtube_search")
def _make_youtube_request(url: str, request_type: str = "search"):
    """
    Make a throttled request to YouTube API.
    
    Args:
        url: The YouTube API URL to request
        request_type: Type of request for logging
    
    Returns:
        Response object or None on failure
    """
    try:
        logger.debug(f"Making YouTube API request: {request_type}")
        response = requests.get(url, timeout=10)
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"YouTube API request failed ({request_type}): {e}")
        return None


def get_top_video_quick(channel_id, api_key, cache_instance=None):
    """Get the top video for a channel with optional caching."""
    if cache_instance:
        return _get_top_video_cached(channel_id, api_key, cache_instance)
    return _get_top_video_uncached(channel_id, api_key)


def _get_top_video_cached(channel_id, api_key, cache_instance):
    """Get top video with caching."""
    @cache_result(cache_instance, CacheConfig.YOUTUBE_VIDEO_CACHE_TIMEOUT, "youtube:top_video")
    def _cached_get(ch_id, key):
        return _get_top_video_uncached(ch_id, key)
    
    return _cached_get(channel_id, api_key)


def _get_top_video_uncached(channel_id, api_key):
    """Get the top video for a channel without caching."""
    url = f"https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet,id&order=viewCount&maxResults=1&type=video"
    resp = _make_youtube_request(url, "top_video_search")
    
    if resp and resp.status_code == 200:
        data = resp.json()
        if data.get('items'):
            video_id = data['items'][0]['id']['videoId']
            video_title = data['items'][0]['snippet']['title']
            stats_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={video_id}&key={api_key}"
            stats_resp = _make_youtube_request(stats_url, "video_stats")
            
            if stats_resp and stats_resp.status_code == 200:
                stats_data = stats_resp.json()
                if stats_data.get('items'):
                    views = stats_data['items'][0]['statistics']['viewCount']
                    return {
                        'video_id': video_id,
                        'views': views,
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'title': video_title
                    }
    return None


def get_channel_stats(channel_id, api_key, cache_instance=None):
    """Get channel statistics with optional caching."""
    if cache_instance:
        return _get_channel_stats_cached(channel_id, api_key, cache_instance)
    return _get_channel_stats_uncached(channel_id, api_key, cache_instance)


def _get_channel_stats_cached(channel_id, api_key, cache_instance):
    """Get channel stats with caching."""
    @cache_result(cache_instance, CacheConfig.YOUTUBE_CHANNEL_CACHE_TIMEOUT, "youtube:channel_stats")
    def _cached_get(ch_id, key):
        return _get_channel_stats_uncached(ch_id, key, cache_instance)
    
    return _cached_get(channel_id, api_key)


def _get_channel_stats_uncached(channel_id, api_key, cache_instance=None):
    """Get channel statistics without caching."""
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet&id={channel_id}&key={api_key}"
    response = _make_youtube_request(url, "channel_stats")
    
    if response and response.status_code == 200:
        data = response.json()
        if data.get('items'):
            stats = data['items'][0]['statistics']
            snippet = data['items'][0]['snippet']
            top_video = get_top_video_quick(channel_id, api_key, cache_instance)
            
            return {
                'title': snippet.get('title'),
                'description': snippet.get('description'),
                'subscribers': format_number(stats.get('subscriberCount', '0')),
                'views': format_number(stats.get('viewCount', '0')),
                'video_count': format_number(stats.get('videoCount', '0')),
                'channel_url': f"https://www.youtube.com/channel/{channel_id}",
                'image_url': snippet.get('thumbnails', {}).get('high', {}).get('url'),
                'top_video_url': top_video['url'] if top_video else None,
                'top_video_views': format_number(top_video['views']) if top_video else None,
                'top_video_title': top_video['title'] if top_video else None
            }
    return None


def get_channel_stats_by_name(channel_name, api_key, cache_instance=None):
    """Search for channel by name and get statistics with optional caching."""
    if cache_instance:
        return _get_channel_stats_by_name_cached(channel_name, api_key, cache_instance)
    return _get_channel_stats_by_name_uncached(channel_name, api_key, cache_instance)


def _get_channel_stats_by_name_cached(channel_name, api_key, cache_instance):
    """Get channel stats by name with caching."""
    @cache_result(cache_instance, CacheConfig.YOUTUBE_CHANNEL_CACHE_TIMEOUT, "youtube:channel_by_name")
    def _cached_get(name, key):
        return _get_channel_stats_by_name_uncached(name, key, cache_instance)
    
    return _cached_get(channel_name, api_key)


def _get_channel_stats_by_name_uncached(channel_name, api_key, cache_instance=None):
    """Search for channel by name and get statistics without caching."""
    search_url = (
        f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={channel_name}&key={api_key}&maxResults=1"
    )
    search_resp = _make_youtube_request(search_url, "channel_search")
    
    if search_resp and search_resp.status_code == 200:
        search_data = search_resp.json()
        if search_data.get('items'):
            channel_id = search_data['items'][0]['snippet']['channelId']
            return get_channel_stats(channel_id, api_key, cache_instance)
    return None
