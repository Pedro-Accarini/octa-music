# Octa Music API Documentation

## Base URL
```
http://localhost:5000/api/v1
```

## Authentication
Currently, the API does not require authentication. Rate limiting is applied to all endpoints.

## Rate Limits
- API endpoints: 20 requests per minute
- Web pages: 30 requests per minute

## Common Response Format

All API responses follow this standard format:

```json
{
  "success": true|false,
  "error": null|"Error message",
  "data": {...}|null,
  "message": "Optional success message"
}
```

## Endpoints

### Health Check

Check the API status and version.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "success": true,
  "error": null,
  "data": {
    "status": "healthy",
    "version": "1.0.0"
  },
  "message": null
}
```

---

### Search Spotify Artist

Search for a Spotify artist by name.

**Endpoint:** `POST /spotify/search`

**Headers:**
- `Content-Type: application/json`

**Request Body:**
```json
{
  "artist_name": "Artist Name"
}
```

**Parameters:**
- `artist_name` (required): Artist name to search (max 100 characters)

**Success Response (200):**
```json
{
  "success": true,
  "error": null,
  "data": {
    "name": "Artist Name",
    "followers": "1,234,567",
    "popularity": 85,
    "image_url": "https://...",
    "genres": "pop, rock",
    "spotify_url": "https://open.spotify.com/artist/..."
  },
  "message": "Artist found successfully"
}
```

**Error Responses:**

404 - Artist Not Found:
```json
{
  "success": false,
  "error": "Artist not found",
  "data": null
}
```

400 - Missing Artist Name:
```json
{
  "success": false,
  "error": "artist_name is required",
  "data": null
}
```

400 - Invalid Content Type:
```json
{
  "success": false,
  "error": "Content-Type must be application/json",
  "data": null
}
```

---

### Search YouTube Channel

Search for a YouTube channel by name.

**Endpoint:** `POST /youtube/search`

**Headers:**
- `Content-Type: application/json`

**Request Body:**
```json
{
  "channel_name": "Channel Name"
}
```

**Parameters:**
- `channel_name` (required): Channel name to search (max 100 characters)

**Success Response (200):**
```json
{
  "success": true,
  "error": null,
  "data": {
    "title": "Channel Name",
    "description": "Channel description...",
    "subscribers": "1000000",
    "views": "50000000",
    "video_count": "500",
    "channel_url": "https://www.youtube.com/channel/...",
    "image_url": "https://...",
    "top_video_url": "https://www.youtube.com/watch?v=...",
    "top_video_views": "5000000",
    "top_video_title": "Video Title"
  },
  "message": "Channel found successfully"
}
```

**Error Responses:**

404 - Channel Not Found:
```json
{
  "success": false,
  "error": "Channel not found",
  "data": null
}
```

400 - Missing Channel Name:
```json
{
  "success": false,
  "error": "channel_name is required",
  "data": null
}
```

---

## Example Usage

### cURL

**Health Check:**
```bash
curl http://localhost:5000/api/v1/health
```

**Search Spotify Artist:**
```bash
curl -X POST http://localhost:5000/api/v1/spotify/search \
  -H "Content-Type: application/json" \
  -d '{"artist_name": "Taylor Swift"}'
```

**Search YouTube Channel:**
```bash
curl -X POST http://localhost:5000/api/v1/youtube/search \
  -H "Content-Type: application/json" \
  -d '{"channel_name": "MrBeast"}'
```

### Python

```python
import requests

# Health check
response = requests.get('http://localhost:5000/api/v1/health')
print(response.json())

# Search Spotify artist
response = requests.post(
    'http://localhost:5000/api/v1/spotify/search',
    json={'artist_name': 'Taylor Swift'}
)
print(response.json())

# Search YouTube channel
response = requests.post(
    'http://localhost:5000/api/v1/youtube/search',
    json={'channel_name': 'MrBeast'}
)
print(response.json())
```

### JavaScript (fetch)

```javascript
// Health check
fetch('http://localhost:5000/api/v1/health')
  .then(response => response.json())
  .then(data => console.log(data));

// Search Spotify artist
fetch('http://localhost:5000/api/v1/spotify/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    artist_name: 'Taylor Swift'
  })
})
  .then(response => response.json())
  .then(data => console.log(data));

// Search YouTube channel
fetch('http://localhost:5000/api/v1/youtube/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    channel_name: 'MrBeast'
  })
})
  .then(response => response.json())
  .then(data => console.log(data));
```

## Error Codes

- `200` - Success
- `400` - Bad Request (invalid input)
- `404` - Not Found (artist/channel not found)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

## CORS

The API supports Cross-Origin Resource Sharing (CORS) for all `/api/*` endpoints with the following configuration:
- Origins: `*` (all origins allowed)
- Methods: `GET`, `POST`, `OPTIONS`
- Headers: `Content-Type`
