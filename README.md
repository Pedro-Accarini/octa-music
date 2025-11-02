# Octa Music

Octa Music is a Flask web application that allows you to search for artists on Spotify and YouTube channels, displaying relevant information such as name, followers, popularity, images, and more.

It features a modern RESTful API, rate limiting, CORS support, and a responsive design system.

## Features

- Search for artists by name using the official Spotify API
- Search for YouTube channels by name using the YouTube Data API
- Display relevant artist and channel information (name, followers, popularity, images, etc.)
- RESTful API with JSON responses
- Rate limiting to prevent abuse
- CORS support for cross-origin requests
- Modern, responsive web interface with dark mode support
- Comprehensive design system with accessibility features (WCAG AA compliant)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Pedro-Accarini/octa-music.git
   cd octa-music
   ```

2. Set up a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. Create a `.env` file:
   ```bash
   # On Windows:
   copy .env.example .env
   # On macOS/Linux:
   cp .env.example .env
   ```

4. Edit the `.env` file with your API credentials (see Configuration below).

## Configuration

The `.env` file must contain your API credentials:

```
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
YOUTUBE_API_KEY=your_youtube_api_key
SECRET_KEY=your_secret_key
```

**Where to get credentials:**
- **Spotify**: Get `SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET` at https://developer.spotify.com/dashboard/applications
- **YouTube**: Get `YOUTUBE_API_KEY` at https://console.cloud.google.com/apis/credentials
- **SECRET_KEY**: Generate a random string for Flask session security

## Environments (dev, pre, prod)

The project supports multiple execution environments (development, preproduction, production) using the `APP_ENV` environment variable.

- For **development**: set `APP_ENV=development`
- For **preproduction**: set `APP_ENV=preproduction`
- For **production**: set `APP_ENV=production`

Flask will automatically load the correct configuration according to the value of `APP_ENV`.

You can create specific `.env` files for each environment, for example:
- `.env.development`
- `.env.preproduction`
- `.env.production`

Make sure your pipeline or execution environment loads the correct file and sets the `APP_ENV` variable.

## How to Run

Example of local execution for development:
```bash
# On Windows:
set APP_ENV=development
python src/main.py

# On macOS/Linux:
export APP_ENV=development
python src/main.py
```

The application will be available at `http://localhost:5000`

## API Documentation

Octa Music provides a RESTful API for programmatic access to Spotify and YouTube search functionality. For complete API documentation, including endpoints, request/response formats, and examples, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md).

**Quick API Example:**
```bash
# Health check
curl http://localhost:5000/api/v1/health

# Search for a Spotify artist
curl -X POST http://localhost:5000/api/v1/spotify/search \
  -H "Content-Type: application/json" \
  -d '{"artist_name": "Taylor Swift"}'
```

## Contributing

Contributions are welcome! Please read the [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

## License

Distributed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Setup

1. **Configure GitHub Secrets:**
   - Go to your repository → Settings → Secrets and variables → Actions.
   - Add `RENDER_API_KEY` and `RENDER_SERVICE_ID` (with the correct `srv-` prefix).

2. **Custom Actions:**
   - Place your custom CI/CD logic in `.github/actions/ci-checks` and `.github/actions/cd-checks`.

3. **Branch Strategy:**
   - Use the branch naming conventions above for feature, bugfix, hotfix, and release branches to trigger the correct workflows.

## Useful Links

- [Render Dashboard](https://dashboard.render.com/web/srv-d03h38idbo4c738clsag/deploys/)
- [Production Site](https://octa-music.onrender.com/)

---

## UI/UX Design System

Octa Music uses a modern, accessible design system built on design tokens. For detailed component documentation, see [COMPONENT_GUIDE.md](COMPONENT_GUIDE.md).

### Key Features

- **Design Tokens**: Centralized color, spacing, typography, and component tokens
- **Accessibility**: WCAG AA compliant with 44px minimum touch targets
- **Responsive**: Tested at 8 breakpoints (320px to 1440px)
- **Dark Mode**: Full dark mode support with optimized contrast
- **Component Library**: Reusable buttons, inputs, cards, and forms

### Quick Start

All styles are built with CSS custom properties (variables). Import in this order:

```html
<link rel="stylesheet" href="/static/css/design-tokens.css">
<link rel="stylesheet" href="/static/css/base.css">
<link rel="stylesheet" href="/static/css/main.css">
```

### Component Examples

**Button**
```html
<button class="btn btn-primary">Search</button>
```

**Input Field**
```html
<input type="text" class="input" placeholder="Enter text">
```

**Card**
```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Title</h3>
  </div>
  <div class="card-body">Content</div>
</div>
```

### Accessibility Features

- ✅ WCAG AA color contrast compliance
- ✅ Keyboard navigation with visible focus indicators
- ✅ 44-48px minimum touch targets on all interactive elements
- ✅ ARIA labels and roles on forms
- ✅ Screen reader friendly markup

### Responsive Breakpoints

- 320px: Mobile Small
- 375px: Mobile Standard
- 412px: Mobile Large
- 480px: Phablet
- 768px: Tablet
- 1024px: Desktop
- 1280px: Desktop Large
- 1440px: Desktop XL

For complete documentation, see [COMPONENT_GUIDE.md](COMPONENT_GUIDE.md).
