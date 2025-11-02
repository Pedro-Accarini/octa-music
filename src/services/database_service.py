"""
Database service for MongoDB connection and operations.
"""
import logging
from typing import Optional
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure, OperationFailure
from flask import current_app

logger = logging.getLogger(__name__)


class DatabaseService:
    """
    MongoDB database service for managing connections and collections.
    """
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db = None
    
    def init_app(self, app):
        """
        Initialize MongoDB connection with Flask app.
        
        Args:
            app: Flask application instance
        """
        mongodb_uri = app.config.get('MONGODB_URI')
        
        if not mongodb_uri:
            logger.warning("MongoDB URI not configured. Authentication features will be disabled.")
            return
        
        try:
            self.client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')
            
            db_name = app.config.get('MONGODB_DB_NAME', 'octa_music')
            self.db = self.client[db_name]
            
            # Create indexes for better performance
            self._create_indexes()
            
            logger.info(f"Successfully connected to MongoDB database: {db_name}")
        except (ConnectionFailure, OperationFailure) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.client = None
            self.db = None
    
    def _create_indexes(self):
        """Create database indexes for optimized queries."""
        if self.db is None:
            return
        
        try:
            # Users collection indexes
            users = self.db.users
            users.create_index([("email", ASCENDING)], unique=True)
            users.create_index([("username", ASCENDING)], unique=True)
            users.create_index([("verification_token", ASCENDING)], sparse=True)
            users.create_index([("reset_token", ASCENDING)], sparse=True)
            
            # Search history collection indexes
            search_history = self.db.search_history
            search_history.create_index([("user_id", ASCENDING)])
            search_history.create_index([("timestamp", ASCENDING)])
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    def get_users_collection(self):
        """Get users collection."""
        if self.db is None:
            return None
        return self.db.users
    
    def get_search_history_collection(self):
        """Get search history collection."""
        if self.db is None:
            return None
        return self.db.search_history
    
    def is_connected(self) -> bool:
        """Check if database is connected."""
        if self.client is None or self.db is None:
            return False
        
        try:
            self.client.admin.command('ping')
            return True
        except:
            return False
    
    def close(self):
        """Close database connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


# Global database service instance
db_service = DatabaseService()
