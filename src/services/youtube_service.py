import requests
import logging

logger = logging.getLogger(__name__)

def get_top_video_quick(channel_id, api_key):
    """Get the top video by view count for a channel.
    
    Args:
        channel_id: YouTube channel ID
        api_key: YouTube API key
        
    Returns:
        dict: Video information or None if not found
    """
    try:
        url = f"https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet,id&order=viewCount&maxResults=1&type=video"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        
        data = resp.json()
        if data.get('items'):
            video_id = data['items'][0]['id']['videoId']
            video_title = data['items'][0]['snippet']['title']
            stats_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={video_id}&key={api_key}"
            stats_resp = requests.get(stats_url, timeout=10)
            stats_resp.raise_for_status()
            
            stats_data = stats_resp.json()
            if stats_data.get('items'):
                views = stats_data['items'][0]['statistics']['viewCount']
                return {
                    'video_id': video_id,
                    'views': views,
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'title': video_title
                }
    except requests.RequestException as e:
        logger.error(f"Error fetching top video: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in get_top_video_quick: {str(e)}")
    
    return None

def get_channel_stats(channel_id, api_key):
    """Get statistics for a YouTube channel.
    
    Args:
        channel_id: YouTube channel ID
        api_key: YouTube API key
        
    Returns:
        dict: Channel statistics or None if not found
    """
    try:
        url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet&id={channel_id}&key={api_key}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data.get('items'):
            stats = data['items'][0]['statistics']
            snippet = data['items'][0]['snippet']
            top_video = get_top_video_quick(channel_id, api_key)
            return {
                'title': snippet.get('title'),
                'description': snippet.get('description'),
                'subscribers': stats.get('subscriberCount'),
                'views': stats.get('viewCount'),
                'video_count': stats.get('videoCount'),
                'channel_url': f"https://www.youtube.com/channel/{channel_id}",
                'image_url': snippet.get('thumbnails', {}).get('high', {}).get('url'),
                'top_video_url': top_video['url'] if top_video else None,
                'top_video_views': top_video['views'] if top_video else None,
                'top_video_title': top_video['title'] if top_video else None
            }
    except requests.RequestException as e:
        logger.error(f"Error fetching channel stats: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in get_channel_stats: {str(e)}")
    
    return None

def get_channel_stats_by_name(channel_name, api_key):
    """Get statistics for a YouTube channel by name.
    
    Args:
        channel_name: YouTube channel name to search for
        api_key: YouTube API key
        
    Returns:
        dict: Channel statistics or None if not found
    """
    try:
        if not channel_name or not channel_name.strip():
            logger.warning("Empty channel name provided")
            return None
            
        search_url = (
            f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={channel_name}&key={api_key}&maxResults=1"
        )
        search_resp = requests.get(search_url, timeout=10)
        search_resp.raise_for_status()
        
        search_data = search_resp.json()
        if search_data.get('items'):
            channel_id = search_data['items'][0]['snippet']['channelId']
            return get_channel_stats(channel_id, api_key)
        
        logger.info(f"No channel found for: {channel_name}")
    except requests.RequestException as e:
        logger.error(f"Error searching channel: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in get_channel_stats_by_name: {str(e)}")
    
    return None
