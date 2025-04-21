# Octa Music

Octa Music is a simple web application built with Flask that allows you to search for artists on Spotify and view information such as name, follower count, popularity, and artist image.  
It is ideal for quickly exploring artist data using the Spotify API.

## Features

- Search for artists by name using the official Spotify API
- Display relevant artist information (name, followers, popularity, image)
- Simple and responsive web interface

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/octa-music.git
   cd octa-music
   ```
2. Run the setup script (Windows):
   ```
   setup.bat
   ```
   Or manually:
   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   copy .env.example .env
   ```
3. Edit the `.env` file with your Spotify credentials.

## Usage

1. Activate the virtual environment:
   ```
   venv\Scripts\activate
   ```
2. Run the application:
   ```
   python src/main.py
   ```
3. Open [http://localhost:5000](http://localhost:5000) in your browser.

## Configuration

The `.env` file must contain your Spotify credentials:

```
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
```

You can obtain these credentials at https://developer.spotify.com/dashboard/applications

## Contributing

Contributions are welcome! Please read the [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

## License

Distributed under the MIT License. See the [LICENSE](LICENSE) file for more details.
