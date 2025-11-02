# Octa Music

Octa Music is a web application built with Flask that allows you to search for artists on Spotify, view artist information, and manage your music exploration experience with a complete user account system.

## Features

### Music Discovery
- Search for artists by name using the official Spotify API
- Display relevant artist information (name, followers, popularity, image)
- Track search history for logged-in users

### User Authentication
- User registration with email verification
- Secure login with username or email
- "Remember Me" for extended sessions (30 days)
- Password reset via email
- Profile management (update username, email, password)
- Session timeout with automatic warnings

### UI/UX
- Simple and responsive web interface
- Full dark mode support
- Toast notifications for user feedback
- Accessible design (WCAG AA compliant)

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

## Authentication System Setup

Octa Music includes a complete authentication system with user registration, login, profile management, password reset, and email verification.

### MongoDB Atlas Setup

The authentication system uses MongoDB Atlas (free tier) for user data storage.

1. **Create MongoDB Atlas Account**
   - Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
   - Sign up for a free account
   - Create a new cluster (M0 Free tier is sufficient)

2. **Create Database User**
   - Navigate to "Database Access" in the left sidebar
   - Click "Add New Database User"
   - Create a user with username and password
   - Grant "Read and write to any database" permission

3. **Configure Network Access**
   - Navigate to "Network Access"
   - Click "Add IP Address"
   - For development: Add your current IP
   - For production: Add `0.0.0.0/0` (allows access from anywhere)

4. **Get Connection String**
   - Navigate to "Database" → "Connect"
   - Choose "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your database user password
   - Replace `<dbname>` with `octa_music`

5. **Add to Environment Variables**
   - Add the connection string to your `.env` file:
   ```
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/octa_music?retryWrites=true&w=majority
   ```

### Email Configuration

The authentication system sends verification and password reset emails.

#### Option 1: Gmail SMTP (Recommended for Development)

1. **Enable 2-Factor Authentication** on your Google account
2. **Generate App-Specific Password**:
   - Go to Google Account Settings → Security
   - Enable 2-Step Verification
   - Go to "App passwords"
   - Generate a new app password for "Mail"
3. **Add to `.env`**:
   ```
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-specific-password
   MAIL_DEFAULT_SENDER=your-email@gmail.com
   ```

#### Option 2: Outlook SMTP

1. **Add to `.env`**:
   ```
   MAIL_SERVER=smtp-mail.outlook.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@outlook.com
   MAIL_PASSWORD=your-password
   MAIL_DEFAULT_SENDER=your-email@outlook.com
   ```

#### Development Mode (Email Console Output)

In development mode, emails are printed to the console instead of being sent. This is enabled by default when `APP_ENV=development`.

To disable console-only mode and actually send emails in development:
```
MAIL_SUPPRESS_SEND=False
```

### Environment Variables

Copy `.env.example` to `.env` and configure the following variables:

**Required for Authentication:**
```
# MongoDB
MONGODB_URI=your_mongodb_connection_string

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Flask
SECRET_KEY=your-secret-key-here
```

**Optional (has defaults):**
```
# Session Configuration
SESSION_COOKIE_SECURE=False  # Set True in production
PERMANENT_SESSION_LIFETIME=4800  # 80 minutes in seconds
REMEMBER_ME_DURATION=2592000  # 30 days in seconds

# Rate Limiting
LOGIN_RATE_LIMIT_PER_MINUTE=3
LOGIN_RATE_LIMIT_PER_HOUR=10
```

### GitHub Secrets Configuration (for Production)

Add these secrets to your GitHub repository for production deployment:

1. Go to your repository → Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `MONGODB_URI`: Your MongoDB connection string
   - `SECRET_KEY`: A strong random secret key
   - `MAIL_USERNAME`: Email account username
   - `MAIL_PASSWORD`: Email account password/app password

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Run the application:**
   ```bash
   python src/main.py
   ```

4. **Access the application:**
   - Open browser to `http://localhost:5000`
   - Register a new account
   - Check console for verification email link (in dev mode)
   - Verify email and login

### API Documentation

For detailed API documentation, see [API_AUTHENTICATION.md](API_AUTHENTICATION.md).

### Authentication Features

- ✅ User Registration with email verification
- ✅ Login with username or email
- ✅ "Remember Me" option (30-day sessions)
- ✅ Password reset via email
- ✅ Profile management (update username, email, password)
- ✅ Session timeout with warnings
- ✅ Rate limiting to prevent brute force attacks
- ✅ Search history tracking for logged-in users
- ✅ Secure password hashing with bcrypt
- ✅ Responsive design with dark mode support

### Security Features

- **Password Security**: Bcrypt hashing with 12 salt rounds
- **Session Security**: HTTPOnly, SameSite cookies
- **Rate Limiting**: Protection against brute force attacks
- **Account Lockout**: 15-minute lockout after 5 failed attempts
- **Token Expiration**: Email verification (24h), Password reset (1h)
- **HTTPS Enforcement**: In production environment

## Contributing

Contributions are welcome! Please read the [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

## License

Copyright (c) 2024 pacca. All Rights Reserved.

This software is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited. See the [LICENSE](LICENSE) file for more details.

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
