#!/usr/bin/env python3
"""Test script to verify the application loads correctly."""

import os
import sys

# Set test environment
os.environ['APP_ENV'] = 'development'
os.environ['SECRET_KEY'] = 'test-secret-key-for-development'
os.environ['MONGODB_URI'] = 'mongodb://localhost:27017/test_db'
os.environ['MAIL_SUPPRESS_SEND'] = 'True'

try:
    print("✅ Testing application imports...")
    from src.main import app
    print("✅ Application imports successful!")
    
    print("\n✅ Testing application context...")
    with app.app_context():
        print(f"   - App name: {app.name}")
        print(f"   - Debug mode: {app.config['DEBUG']}")
        print(f"   - Environment: {os.getenv('APP_ENV')}")
        print("✅ Application context works!")
    
    print("\n✅ Testing registered blueprints...")
    for blueprint in app.blueprints:
        print(f"   - {blueprint}")
    print("✅ Blueprints registered successfully!")
    
    print("\n✅ Testing routes...")
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(str(rule))
    print(f"   - Total routes: {len(routes)}")
    auth_routes = [r for r in routes if '/api/auth' in r or'/api/profile' in r]
    print(f"   - Auth routes: {len(auth_routes)}")
    for route in sorted(auth_routes):
        print(f"     {route}")
    print("✅ Routes configured successfully!")
    
    print("\n" + "="*60)
    print("🎉 ALL TESTS PASSED! Application is ready to run.")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
