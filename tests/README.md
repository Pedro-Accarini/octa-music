# Tests Directory

This directory contains the comprehensive testing suite for Octa Music.

## Structure

```
tests/
├── __init__.py                     # Test package initialization
├── conftest.py                     # Shared pytest fixtures and configuration
├── test_main.py                    # Legacy tests (kept for backward compatibility)
├── unit/                           # Unit tests
│   ├── __init__.py
│   ├── test_config.py              # Configuration tests
│   └── test_routes.py              # Flask route tests
└── integration/                    # Integration tests
    ├── __init__.py
    ├── test_spotify_service.py     # Spotify API integration tests
    └── test_youtube_service.py     # YouTube API integration tests
```

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Unit Tests Only
```bash
pytest tests/unit/
```

### Run Integration Tests Only
```bash
pytest tests/integration/
```

### Run with Coverage Report
```bash
pytest tests/ --cov=src --cov-report=term-missing
```

### Run with HTML Coverage Report
```bash
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

### Run Specific Test File
```bash
pytest tests/unit/test_routes.py -v
```

### Run Specific Test Class
```bash
pytest tests/unit/test_routes.py::TestHomeRoute -v
```

### Run Specific Test Function
```bash
pytest tests/unit/test_routes.py::TestHomeRoute::test_home_get_request -v
```

## Test Coverage

Current test coverage: **97%** (exceeds the 80% requirement)

Coverage breakdown:
- `src/__init__.py`: 100%
- `src/config.py`: 100%
- `src/main.py`: 93%
- `src/services/spotify_service.py`: 100%
- `src/services/youtube_service.py`: 100%

## Test Categories

### Unit Tests (30 tests)
- **Config Tests**: Test configuration classes and environment variable loading
- **Route Tests**: Test Flask routes (home, login), session management, and error handling

### Integration Tests (25 tests)
- **Spotify Service Tests**: Test Spotify API integration with mocked responses
- **YouTube Service Tests**: Test YouTube API integration with mocked HTTP responses

### Legacy Tests (4 tests)
- Kept for backward compatibility with existing CI/CD

## Writing New Tests

### Unit Test Example
```python
import pytest
from src.main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_new_feature(client):
    response = client.get('/new-endpoint')
    assert response.status_code == 200
```

### Integration Test Example
```python
import responses
from src.services.youtube_service import get_channel_stats

@responses.activate
def test_youtube_api():
    responses.add(
        responses.GET,
        'https://www.googleapis.com/youtube/v3/channels',
        json={'items': [...]},
        status=200
    )
    result = get_channel_stats('channel_id', 'api_key')
    assert result is not None
```

## CI/CD Integration

Tests are automatically run on:
- Push to `main`, `development`, `feature/*`, `bugfix/*`, `hotfix/*`, `release/*` branches
- Pull requests to these branches

The CI workflow:
1. Sets up Python environment
2. Installs dependencies
3. Runs all tests with coverage
4. Uploads coverage reports as artifacts
5. Fails if coverage < 80%

## Dependencies

Testing dependencies (in `requirements.txt`):
- `pytest`: Test framework
- `pytest-cov`: Coverage reporting
- `pytest-mock`: Mocking utilities
- `responses`: HTTP response mocking for API tests

## Configuration

Test configuration is in `pytest.ini`:
- Minimum coverage: 80%
- Coverage reports: terminal, HTML, XML
- Test discovery patterns
- Markers for test categorization
