import os
import sys
import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set test environment variables
os.environ['SPOTIPY_CLIENT_ID'] = 'test_client_id'
os.environ['SPOTIPY_CLIENT_SECRET'] = 'test_client_secret'
os.environ['APP_ENV'] = 'testing'


@pytest.fixture(scope='session')
def app():
    """Create and configure a Flask app instance for testing."""
    from src.main import app as flask_app
    flask_app.config['TESTING'] = True
    flask_app.config['SECRET_KEY'] = 'test_secret_key'
    return flask_app


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test runner for CLI commands."""
    return app.test_cli_runner()
