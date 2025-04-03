"""
MongoDB-compatible models for the chess application.
These models provide Flask-Login compatibility with MongoDB documents.
"""

from flask_login import UserMixin
from bson.objectid import ObjectId
from chess_app.db.mongo_db import get_user_by_id

class User(UserMixin):
    """User model compatible with Flask-Login but backed by MongoDB."""
    
    def __init__(self, user_doc):
        """
        Initialize a User object from a MongoDB document.
        
        Args:
            user_doc: MongoDB user document
        """
        self.id = str(user_doc["_id"])
        self.doc = user_doc
        self.username = user_doc["username"]
        
        # Game statistics
        self.games_played = user_doc.get("games_played", 0)
        self.wins = user_doc.get("wins", 0)
        self.losses = user_doc.get("losses", 0)
        self.draws = user_doc.get("draws", 0)
    
    def get_id(self):
        """Get the user ID as a string for Flask-Login."""
        return self.id
    
    def check_password(self, password):
        """Check if the provided password matches the hash."""
        from chess_app.db.mongo_db import check_password
        return check_password(self.doc, password)
    
    def get_win_percentage(self):
        """Calculate the user's win percentage."""
        if self.games_played == 0:
            return 0
        return (self.wins / self.games_played) * 100
    
    @staticmethod
    def load_user(user_id):
        """Load a user by ID for Flask-Login."""
        user_doc = get_user_by_id(user_id)
        if user_doc:
            return User(user_doc)
        return None