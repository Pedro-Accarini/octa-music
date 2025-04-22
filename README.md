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

# Octa Music CI/CD

This project uses GitHub Actions for CI/CD with two main workflows:

## Workflows

### 1. Integration Workflow (`.github/workflows/Integration.yml`)

Runs on pushes and pull requests to the following branches:
- `main`
- `development`
- `feature/*`
- `bugfix/*`
- `hotfix/*`
- `release/*`

**Job: `ci-checks`**
- Checks out the code.
- Runs custom CI checks using `.github/actions/ci-checks`.

### 2. Deployment Workflow (`.github/workflows/Deployment.yml`)

Runs on pushes to the `main` branch.

**Job: `deploy`**
- Checks out the code.
- Runs custom CD checks using `.github/actions/cd-checks`.
- Deploys to [Render](https://render.com/) using the Render API.

#### Render Deployment

- Requires two GitHub secrets:
  - `RENDER_API_KEY`: Your Render API key.
  - `RENDER_SERVICE_ID`: Your Render service ID (must start with `srv-`, e.g., `srv-d03h38idbo4c738clsag`).
- The deployment step triggers a deployment on Render and checks for errors in the API response.

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
