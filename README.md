# Octa Music

[![Integration](https://github.com/Pedro-Accarini/octa-music/actions/workflows/Integration.yml/badge.svg)](https://github.com/Pedro-Accarini/octa-music/actions/workflows/Integration.yml)
[![Deployment](https://github.com/Pedro-Accarini/octa-music/actions/workflows/Deployment.yml/badge.svg)](https://github.com/Pedro-Accarini/octa-music/actions/workflows/Deployment.yml)
[![CodeQL](https://github.com/Pedro-Accarini/octa-music/actions/workflows/codeql.yml/badge.svg)](https://github.com/Pedro-Accarini/octa-music/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

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

Your pipeline should set `APP_ENV` according to the branch (e.g.: `main` → production, `development` → development, `release/*` → preproduction).

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

### Quick Start for Contributors

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/octa-music.git`
3. Create a branch: `git checkout -b feature/your-feature`
4. Make your changes and test locally: `./scripts/local-ci.sh` (or `scripts\local-ci.bat` on Windows)
5. Commit your changes: `git commit -m "feat: add amazing feature"`
6. Push to your fork: `git push origin feature/your-feature`
7. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

Distributed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

# CI/CD Pipeline

This project uses GitHub Actions for a robust CI/CD pipeline with multiple workflows:

## Workflows

### 1. Integration Workflow (`.github/workflows/Integration.yml`)

**Triggers:** Pushes and pull requests to `main`, `development`, `feature/*`, `bugfix/*`, `hotfix/*`, `release/*`

**Jobs:**
- **Quality Checks**: Code formatting (Black), linting (Flake8), static analysis (Pylint), type checking (Mypy)
- **Test Matrix**: Tests across Python 3.8-3.12 on Ubuntu, Windows, and macOS
- **Integration Tests**: Full integration testing with coverage reporting

### 2. Deployment Workflow (`.github/workflows/Deployment.yml`)

**Triggers:** Pushes to `main` branch

**Jobs:**
- **Pre-Deployment Checks**: Validates code quality and runs tests
- **Deploy**: Deploys to Render with health checks and status tracking
- **Publish Tag**: Creates Git tags for version tracking
- **Deployment Summary**: Generates comprehensive deployment report

### 3. CodeQL Security Analysis (`.github/workflows/codeql.yml`)

**Triggers:** Pushes, pull requests, and weekly schedule (Mondays)

**Features:**
- Automated security vulnerability scanning
- Python and JavaScript code analysis
- Security-extended query suite

## Pipeline Features

### Security
- ✅ CodeQL security scanning
- ✅ Dependabot for dependency updates
- ✅ Secret scanning protection
- ✅ Security policy and vulnerability reporting

### Quality
- ✅ Code formatting checks (Black)
- ✅ Linting (Flake8, Pylint)
- ✅ Type checking (Mypy)
- ✅ Code coverage reporting

### Robustness
- ✅ Matrix testing (Python 3.8-3.12, Ubuntu/Windows/macOS)
- ✅ Dependency caching for faster builds
- ✅ Timeout configurations
- ✅ Health checks and rollback capability
- ✅ Deployment status tracking

### Developer Experience
- ✅ Pre-commit hooks (`.pre-commit-config.yaml`)
- ✅ Local CI scripts (`scripts/local-ci.sh`, `scripts/local-ci.bat`)
- ✅ Comprehensive workflow summaries
- ✅ Clear error messages and logs

## Setup

1. **Configure GitHub Secrets:**
   - Go to your repository → Settings → Secrets and variables → Actions
   - Add `RENDER_API_KEY`: Your Render API key
   - Add `RENDER_SERVICE_ID`: Your Render service ID (format: `srv-xxxxx`)

2. **Enable Branch Protection:**
   - Go to Settings → Branches → Add rule for `main`
   - Require pull request reviews
   - Require status checks to pass (Integration workflow)
   - Require branches to be up to date

3. **Configure Dependabot:**
   - Already configured in `.github/dependabot.yml`
   - Automatically creates PRs for dependency updates

4. **Install Pre-commit Hooks (for developers):**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Local Development

Run local CI checks before pushing:

**Linux/macOS:**
```bash
./scripts/local-ci.sh
```

**Windows:**
```cmd
scripts\local-ci.bat
```

## Useful Links

- [Render Dashboard](https://dashboard.render.com/web/srv-d03h38idbo4c738clsag/deploys/)
- [Production Site](https://octa-music.onrender.com/)

---
