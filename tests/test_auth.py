import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ['SPOTIPY_CLIENT_ID'] = 'dummy'
os.environ['SPOTIPY_CLIENT_SECRET'] = 'dummy'

from src.main import app, db, bcrypt
from src.models.user import User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def registered_user(client):
    """Create a test user in the database"""
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        user = User(email='test@example.com', password=hashed_password)
        db.session.add(user)
        db.session.commit()
    return user

def test_register_get(client):
    """Test GET request to register page"""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Create Account' in response.data

def test_register_successful(client):
    """Test successful user registration"""
    response = client.post('/register', data={
        'email': 'newuser@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Registration successful' in response.data
    
    with app.app_context():
        user = User.query.filter_by(email='newuser@example.com').first()
        assert user is not None
        assert user.email == 'newuser@example.com'

def test_register_password_mismatch(client):
    """Test registration with mismatched passwords"""
    response = client.post('/register', data={
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'differentpassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Passwords do not match' in response.data

def test_register_short_password(client):
    """Test registration with password too short"""
    response = client.post('/register', data={
        'email': 'test@example.com',
        'password': '12345',
        'confirm_password': '12345'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Password must be at least 6 characters' in response.data

def test_register_existing_email(client, registered_user):
    """Test registration with already existing email"""
    response = client.post('/register', data={
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Email already registered' in response.data

def test_login_get(client):
    """Test GET request to login page"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Welcome back' in response.data

def test_login_successful(client, registered_user):
    """Test successful login"""
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Welcome back' in response.data

def test_login_invalid_email(client, registered_user):
    """Test login with invalid email"""
    response = client.post('/login', data={
        'email': 'wrong@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Invalid email or password' in response.data

def test_login_invalid_password(client, registered_user):
    """Test login with invalid password"""
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Invalid email or password' in response.data

def test_logout(client, registered_user):
    """Test logout functionality"""
    # First login
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    # Then logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'logged out successfully' in response.data

def test_logout_requires_login(client):
    """Test that logout requires being logged in"""
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please log in' in response.data

def test_register_redirect_if_authenticated(client, registered_user):
    """Test that authenticated users are redirected from register page"""
    # Login first
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    # Try to access register
    response = client.get('/register', follow_redirects=True)
    assert response.status_code == 200

def test_login_redirect_if_authenticated(client, registered_user):
    """Test that authenticated users are redirected from login page"""
    # Login first
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    # Try to access login again
    response = client.get('/login', follow_redirects=True)
    assert response.status_code == 200
