# Octa Music

Octa Music is a simple web application built with Flask that allows you to search for artists on Spotify and view information such as name, follower count, popularity, and artist image.
  
It is ideal for quickly exploring artist data using the Spotify API.

## Features

- Search for artists by name using the official Spotify API
- Display relevant artist information (name, followers, popularity, image)
- Simple and responsive web interface

## Installation

1. Run 
   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   copy .env.example .env
   ```
3. Edit the `.env` file with your Spotify credentials.

## Configuration

The `.env` file must contain your Spotify credentials:

```
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
```

You can obtain these credentials at https://developer.spotify.com/dashboard/applications

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

Example of local execution for development:
```sh
set APP_ENV=development
python src/main.py
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
