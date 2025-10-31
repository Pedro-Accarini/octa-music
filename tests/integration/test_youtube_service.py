import pytest
import responses
from unittest.mock import patch, MagicMock

from src.services.youtube_service import (
    format_number,
    get_top_video_quick,
    get_channel_stats,
    get_channel_stats_by_name
)


class TestFormatNumber:
    """Test cases for the format_number utility function."""

    def test_format_number_with_integer(self):
        """Test formatting a valid integer string."""
        result = format_number('1000')
        assert result == '1,000'

    def test_format_number_with_large_number(self):
        """Test formatting a large number."""
        result = format_number('1234567')
        assert result == '1,234,567'

    def test_format_number_with_small_number(self):
        """Test formatting a small number."""
        result = format_number('100')
        assert result == '100'

    def test_format_number_with_invalid_input(self):
        """Test formatting with invalid input."""
        result = format_number('invalid')
        assert result == 'invalid'

    def test_format_number_with_none(self):
        """Test formatting with None."""
        result = format_number(None)
        assert result is None


class TestGetTopVideoQuick:
    """Test cases for get_top_video_quick function."""

    @responses.activate
    def test_get_top_video_success(self):
        """Test successful retrieval of top video."""
        channel_id = 'UC_test_channel'
        api_key = 'test_api_key'
        
        # Mock search response
        search_response = {
            'items': [{
                'id': {'videoId': 'test_video_id'},
                'snippet': {'title': 'Test Video'}
            }]
        }
        
        # Mock video stats response
        stats_response = {
            'items': [{
                'statistics': {'viewCount': '1000000'}
            }]
        }
        
        responses.add(
            responses.GET,
            f'https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet,id&order=viewCount&maxResults=1&type=video',
            json=search_response,
            status=200
        )
        
        responses.add(
            responses.GET,
            f'https://www.googleapis.com/youtube/v3/videos?part=statistics&id=test_video_id&key={api_key}',
            json=stats_response,
            status=200
        )
        
        result = get_top_video_quick(channel_id, api_key)
        
        assert result is not None
        assert result['video_id'] == 'test_video_id'
        assert result['views'] == '1000000'
        assert result['title'] == 'Test Video'
        assert result['url'] == 'https://www.youtube.com/watch?v=test_video_id'

    @responses.activate
    def test_get_top_video_no_videos(self):
        """Test when channel has no videos."""
        channel_id = 'UC_empty_channel'
        api_key = 'test_api_key'
        
        search_response = {'items': []}
        
        responses.add(
            responses.GET,
            f'https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet,id&order=viewCount&maxResults=1&type=video',
            json=search_response,
            status=200
        )
        
        result = get_top_video_quick(channel_id, api_key)
        
        assert result is None

    @responses.activate
    def test_get_top_video_api_error(self):
        """Test handling of API error."""
        channel_id = 'UC_test_channel'
        api_key = 'test_api_key'
        
        responses.add(
            responses.GET,
            f'https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet,id&order=viewCount&maxResults=1&type=video',
            json={'error': 'API Error'},
            status=400
        )
        
        result = get_top_video_quick(channel_id, api_key)
        
        assert result is None


class TestGetChannelStats:
    """Test cases for get_channel_stats function."""

    @responses.activate
    def test_get_channel_stats_success(self):
        """Test successful retrieval of channel statistics."""
        channel_id = 'UC_test_channel'
        api_key = 'test_api_key'
        
        # Mock channel stats response
        channel_response = {
            'items': [{
                'statistics': {
                    'subscriberCount': '1000000',
                    'viewCount': '50000000',
                    'videoCount': '100'
                },
                'snippet': {
                    'title': 'Test Channel',
                    'description': 'Test Description',
                    'thumbnails': {
                        'high': {'url': 'http://example.com/thumb.jpg'}
                    }
                }
            }]
        }
        
        # Mock top video search
        search_response = {
            'items': [{
                'id': {'videoId': 'top_video_id'},
                'snippet': {'title': 'Top Video'}
            }]
        }
        
        # Mock top video stats
        stats_response = {
            'items': [{
                'statistics': {'viewCount': '5000000'}
            }]
        }
        
        responses.add(
            responses.GET,
            f'https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet&id={channel_id}&key={api_key}',
            json=channel_response,
            status=200
        )
        
        responses.add(
            responses.GET,
            f'https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet,id&order=viewCount&maxResults=1&type=video',
            json=search_response,
            status=200
        )
        
        responses.add(
            responses.GET,
            f'https://www.googleapis.com/youtube/v3/videos?part=statistics&id=top_video_id&key={api_key}',
            json=stats_response,
            status=200
        )
        
        result = get_channel_stats(channel_id, api_key)
        
        assert result is not None
        assert result['title'] == 'Test Channel'
        assert result['description'] == 'Test Description'
        assert result['subscribers'] == '1,000,000'
        assert result['views'] == '50,000,000'
        assert result['video_count'] == '100'
        assert result['channel_url'] == f'https://www.youtube.com/channel/{channel_id}'
        assert result['image_url'] == 'http://example.com/thumb.jpg'
        assert result['top_video_url'] == 'https://www.youtube.com/watch?v=top_video_id'
        assert result['top_video_views'] == '5,000,000'
        assert result['top_video_title'] == 'Top Video'

    @responses.activate
    def test_get_channel_stats_no_channel(self):
        """Test when channel is not found."""
        channel_id = 'UC_nonexistent'
        api_key = 'test_api_key'
        
        channel_response = {'items': []}
        
        responses.add(
            responses.GET,
            f'https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet&id={channel_id}&key={api_key}',
            json=channel_response,
            status=200
        )
        
        result = get_channel_stats(channel_id, api_key)
        
        assert result is None

    @responses.activate
    def test_get_channel_stats_api_error(self):
        """Test handling of API error."""
        channel_id = 'UC_test_channel'
        api_key = 'test_api_key'
        
        responses.add(
            responses.GET,
            f'https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet&id={channel_id}&key={api_key}',
            json={'error': 'API Error'},
            status=400
        )
        
        result = get_channel_stats(channel_id, api_key)
        
        assert result is None

    @responses.activate
    def test_get_channel_stats_no_top_video(self):
        """Test when channel has no top video."""
        channel_id = 'UC_test_channel'
        api_key = 'test_api_key'
        
        channel_response = {
            'items': [{
                'statistics': {
                    'subscriberCount': '1000',
                    'viewCount': '5000',
                    'videoCount': '0'
                },
                'snippet': {
                    'title': 'New Channel',
                    'description': 'New Description',
                    'thumbnails': {
                        'high': {'url': 'http://example.com/new.jpg'}
                    }
                }
            }]
        }
        
        search_response = {'items': []}
        
        responses.add(
            responses.GET,
            f'https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet&id={channel_id}&key={api_key}',
            json=channel_response,
            status=200
        )
        
        responses.add(
            responses.GET,
            f'https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet,id&order=viewCount&maxResults=1&type=video',
            json=search_response,
            status=200
        )
        
        result = get_channel_stats(channel_id, api_key)
        
        assert result is not None
        assert result['top_video_url'] is None
        assert result['top_video_views'] is None
        assert result['top_video_title'] is None


class TestGetChannelStatsByName:
    """Test cases for get_channel_stats_by_name function."""

    @responses.activate
    def test_get_channel_stats_by_name_success(self):
        """Test successful retrieval of channel stats by name."""
        channel_name = 'Test Channel'
        api_key = 'test_api_key'
        channel_id = 'UC_found_channel'
        
        # Mock search response
        search_response = {
            'items': [{
                'snippet': {'channelId': channel_id}
            }]
        }
        
        # Mock channel stats response
        channel_response = {
            'items': [{
                'statistics': {
                    'subscriberCount': '2000',
                    'viewCount': '10000',
                    'videoCount': '5'
                },
                'snippet': {
                    'title': 'Test Channel',
                    'description': 'Test',
                    'thumbnails': {
                        'high': {'url': 'http://example.com/test.jpg'}
                    }
                }
            }]
        }
        
        # Mock top video search
        top_video_search = {'items': []}
        
        responses.add(
            responses.GET,
            f'https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={channel_name}&key={api_key}&maxResults=1',
            json=search_response,
            status=200
        )
        
        responses.add(
            responses.GET,
            f'https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet&id={channel_id}&key={api_key}',
            json=channel_response,
            status=200
        )
        
        responses.add(
            responses.GET,
            f'https://www.googleapis.com/youtube/v3/search?key={api_key}&channelId={channel_id}&part=snippet,id&order=viewCount&maxResults=1&type=video',
            json=top_video_search,
            status=200
        )
        
        result = get_channel_stats_by_name(channel_name, api_key)
        
        assert result is not None
        assert result['title'] == 'Test Channel'

    @responses.activate
    def test_get_channel_stats_by_name_not_found(self):
        """Test when channel name is not found."""
        channel_name = 'Nonexistent Channel'
        api_key = 'test_api_key'
        
        search_response = {'items': []}
        
        responses.add(
            responses.GET,
            f'https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={channel_name}&key={api_key}&maxResults=1',
            json=search_response,
            status=200
        )
        
        result = get_channel_stats_by_name(channel_name, api_key)
        
        assert result is None

    @responses.activate
    def test_get_channel_stats_by_name_api_error(self):
        """Test handling of API error in channel search."""
        channel_name = 'Test Channel'
        api_key = 'test_api_key'
        
        responses.add(
            responses.GET,
            f'https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={channel_name}&key={api_key}&maxResults=1',
            json={'error': 'API Error'},
            status=400
        )
        
        result = get_channel_stats_by_name(channel_name, api_key)
        
        assert result is None
