import requests

def format_number(num_str):
    """Format numbers with thousand separators."""
    try:
        num = int(num_str)
        return f"{num:,}"
    except (ValueError, TypeError):
        return num_str

def get_top_video_quick(channel_id, api_key):
    url = f"https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet,id&order=viewCount&maxResults=1&type=video"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        if data['items']:
            video_id = data['items'][0]['id']['videoId']
            video_title = data['items'][0]['snippet']['title']
            stats_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={video_id}&key={api_key}"
            stats_resp = requests.get(stats_url)
            if stats_resp.status_code == 200:
                stats_data = stats_resp.json()
                if stats_data['items']:
                    views = stats_data['items'][0]['statistics']['viewCount']
                    return {
                        'video_id': video_id,
                        'views': views,
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'title': video_title
                    }
    return None

def get_channel_stats(channel_id, api_key):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet&id={channel_id}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['items']:
            stats = data['items'][0]['statistics']
            snippet = data['items'][0]['snippet']
            top_video = get_top_video_quick(channel_id, api_key)
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

def get_channel_stats_by_name(channel_name, api_key):
    search_url = (
        f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={channel_name}&key={api_key}&maxResults=1"
    )
    search_resp = requests.get(search_url)
    if search_resp.status_code == 200:
        search_data = search_resp.json()
        if search_data['items']:
            channel_id = search_data['items'][0]['snippet']['channelId']
            return get_channel_stats(channel_id, api_key)
    return None
