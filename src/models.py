from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Playlist(db.Model):
    __tablename__ = 'playlists'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with songs
    songs = db.relationship('PlaylistSong', back_populates='playlist', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'song_count': len(self.songs)
        }

class PlaylistSong(db.Model):
    __tablename__ = 'playlist_songs'
    
    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id'), nullable=False)
    spotify_track_id = db.Column(db.String(100), nullable=False)
    track_name = db.Column(db.String(200), nullable=False)
    artist_name = db.Column(db.String(200), nullable=False)
    album_name = db.Column(db.String(200), nullable=True)
    duration_ms = db.Column(db.Integer, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    spotify_url = db.Column(db.String(500), nullable=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with playlist
    playlist = db.relationship('Playlist', back_populates='songs')
    
    def to_dict(self):
        return {
            'id': self.id,
            'spotify_track_id': self.spotify_track_id,
            'track_name': self.track_name,
            'artist_name': self.artist_name,
            'album_name': self.album_name,
            'duration_ms': self.duration_ms,
            'image_url': self.image_url,
            'spotify_url': self.spotify_url,
            'added_at': self.added_at.isoformat() if self.added_at else None
        }
