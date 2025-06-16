import os

class Config:
    DEBUG = False
    TESTING = False
    SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
    SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')

class DevelopmentConfig(Config):
    DEBUG = True

class PreproductionConfig(Config):
    DEBUG = False

class ProductionConfig(Config):
    DEBUG = False
