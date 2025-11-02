# 🎵 Octa Music

**A place to register, share your music preferences, and explore artist stats.**

Octa Music connects you with your favorite artists through Spotify data. Create an account, search for artists, and discover detailed statistics about the music you love.

🌐 **[Live Site](https://octa-music.onrender.com/)**

---

## ✨ What You Can Do

- 🔍 **Search Artists** - Find any artist on Spotify
- 📊 **View Stats** - See follower counts, popularity scores, and more
- 💾 **Track History** - Your searches are saved when you're logged in
- 👤 **Manage Profile** - Update your account settings anytime
- 🌙 **Dark Mode** - Full dark mode support

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Spotify Developer Account ([Get one here](https://developer.spotify.com/dashboard))
- MongoDB Atlas Account ([Free tier](https://www.mongodb.com/cloud/atlas))

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Pedro-Accarini/octa-music.git
   cd octa-music
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials (see below)
   ```

4. **Run the application**
   ```bash
   python src/main.py
   ```

5. **Open your browser**
   ```
   http://localhost:5000
   ```

---

## ⚙️ Configuration

### Required Environment Variables

Create a `.env` file with the following:

```bash
# Spotify API (https://developer.spotify.com/dashboard)
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret

# MongoDB (https://www.mongodb.com/cloud/atlas)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/octa_music

# Email (for account verification)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Flask Secret (generate a random string)
SECRET_KEY=your-random-secret-key
```

### Getting API Keys

**Spotify:**
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Copy Client ID and Client Secret

**MongoDB:**
1. Sign up at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Get your connection string

**Email (Gmail):**
1. Enable 2-Factor Authentication on your Google account
2. Generate an [App Password](https://myaccount.google.com/apppasswords)
3. Use this password in `.env`

---

## 📚 Documentation

- **[API Documentation](API_DOCUMENTATION.md)** - REST API reference
- **[Component Guide](COMPONENT_GUIDE.md)** - UI/UX design system
- **[Authentication API](API_AUTHENTICATION.md)** - Auth endpoints


---

## 🛠️ Tech Stack

- **Backend:** Flask (Python)
- **Database:** MongoDB Atlas
- **API:** Spotify Web API
- **Deployment:** Render
- **CI/CD:** GitHub Actions

---

## 🤝 Contributing

Contributions are welcome! Please read the [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

---

## 📄 License

Copyright (c) 2024 pacca. All Rights Reserved.

This software is proprietary and confidential. See the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ for music lovers**
