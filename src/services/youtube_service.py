import requests

def get_channel_stats(channel_id, api_key):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet&id={channel_id}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['items']:
            stats = data['items'][0]['statistics']
            snippet = data['items'][0]['snippet']
            return {
                'title': snippet.get('title'),
                'description': snippet.get('description'),
                'subscribers': stats.get('subscriberCount'),
                'views': stats.get('viewCount'),
                'video_count': stats.get('videoCount'),
                'channel_url': f"https://www.youtube.com/channel/{channel_id}"
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
