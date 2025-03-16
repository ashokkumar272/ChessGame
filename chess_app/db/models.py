"""
Database models for the chess application.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    """User model for authentication and tracking game statistics."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Game statistics
    games_played = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    draws = db.Column(db.Integer, default=0)
    
    # Relationships
    games = db.relationship('Game', backref='player', lazy='dynamic')
    
    def set_password(self, password):
        """Set the user's password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)
    
    def get_win_percentage(self):
        """Calculate the user's win percentage."""
        if self.games_played == 0:
            return 0
        return (self.wins / self.games_played) * 100
    
    def update_stats(self, result):
        """
        Update the user's statistics based on game result.
        
        Args:
            result: Game result ('win', 'loss', 'draw')
        """
        self.games_played += 1
        
        if result == 'win':
            self.wins += 1
        elif result == 'loss':
            self.losses += 1
        elif result == 'draw':
            self.draws += 1
    
    def __repr__(self):
        return f'<User {self.username}>'


class Game(db.Model):
    """Game model for storing game history."""
    
    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    result = db.Column(db.String(10), nullable=True)  # 'win', 'loss', 'draw'
    difficulty = db.Column(db.String(10), nullable=False, default='medium')
    moves = db.Column(db.Text, nullable=True)  # Stored as JSON string
    final_fen = db.Column(db.String(100), nullable=True)
    
    def __repr__(self):
        return f'<Game {self.id} - {self.user_id}>'


class SavedGame(db.Model):
    """Model for storing saved game states."""
    
    __tablename__ = 'saved_games'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    fen = db.Column(db.String(100), nullable=False)
    moves = db.Column(db.Text, nullable=True)  # Stored as JSON string
    difficulty = db.Column(db.String(10), nullable=False, default='medium')
    
    def __repr__(self):
        return f'<SavedGame {self.id} - {self.name}>' 