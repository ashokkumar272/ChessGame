"""
MongoDB database connection and helper functions for the chess application.
"""

import os
from datetime import datetime
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

# MongoDB connection instance
mongo = PyMongo()

def init_app(app):
    """Initialize the MongoDB connection with the Flask app."""
    app.config["MONGO_URI"] = "mongodb://localhost:27017/chess_app"
    mongo.init_app(app)
    
    # Create indexes for better query performance
    with app.app_context():
        # Create unique index on username
        mongo.db.users.create_index("username", unique=True)
        # Create index for game queries
        mongo.db.games.create_index("user_id")
        mongo.db.saved_games.create_index("user_id")

# User-related functions
def get_user_by_id(user_id):
    """Get a user by ID."""
    if isinstance(user_id, str):
        try:
            user_id = ObjectId(user_id)
        except:
            return None
    return mongo.db.users.find_one({"_id": user_id})

def get_user_by_username(username):
    """Get a user by username."""
    return mongo.db.users.find_one({"username": username})

def create_user(username, password):
    """Create a new user."""
    user_data = {
        "username": username,
        "password_hash": generate_password_hash(password),
        "created_at": datetime.utcnow(),
        "games_played": 0,
        "wins": 0,
        "losses": 0,
        "draws": 0
    }
    result = mongo.db.users.insert_one(user_data)
    return result.inserted_id

def check_password(user, password):
    """Check if the provided password matches the user's hash."""
    if not user or "password_hash" not in user:
        return False
    return check_password_hash(user["password_hash"], password)

def update_user_stats(user_id, result):
    """Update a user's game statistics."""
    if isinstance(user_id, str):
        try:
            user_id = ObjectId(user_id)
        except:
            return False
            
    # Increment the appropriate stats based on game result
    update = {
        "$inc": {
            "games_played": 1
        }
    }
    
    if result == "win":
        update["$inc"]["wins"] = 1
    elif result == "loss":
        update["$inc"]["losses"] = 1
    elif result == "draw":
        update["$inc"]["draws"] = 1
    
    result = mongo.db.users.update_one({"_id": user_id}, update)
    return result.modified_count > 0

# Game-related functions
def save_game_record(user_id, game_data):
    """Save a completed game record."""
    if isinstance(user_id, str):
        try:
            user_id = ObjectId(user_id)
        except:
            return None
            
    game_doc = {
        "user_id": user_id,
        "start_time": game_data.get("start_time", datetime.utcnow()),
        "end_time": game_data.get("end_time", datetime.utcnow()),
        "result": game_data.get("result"),
        "difficulty": game_data.get("difficulty", "medium"),
        "moves": game_data.get("moves", []),
        "final_fen": game_data.get("final_fen")
    }
    
    result = mongo.db.games.insert_one(game_doc)
    return result.inserted_id

def get_user_games(user_id, limit=None):
    """Get a user's game history."""
    if isinstance(user_id, str):
        try:
            user_id = ObjectId(user_id)
        except:
            return []
    
    query = {"user_id": user_id}
    cursor = mongo.db.games.find(query).sort("end_time", -1)
    
    if limit:
        cursor = cursor.limit(limit)
        
    return list(cursor)

def get_game_by_id(game_id):
    """Get a game by its ID."""
    try:
        if isinstance(game_id, str):
            game_id = ObjectId(game_id)
        return mongo.db.games.find_one({"_id": game_id})
    except:
        return None

# Saved Game functions
def save_game_state(user_id, game_data):
    """Save a game state for future continuation."""
    if isinstance(user_id, str):
        try:
            user_id = ObjectId(user_id)
        except:
            return None
            
    saved_game = {
        "user_id": user_id,
        "name": game_data.get("name", f"Game_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"),
        "created_at": datetime.utcnow(),
        "fen": game_data.get("fen"),
        "moves": game_data.get("moves", []),
        "difficulty": game_data.get("difficulty", "medium")
    }
    
    result = mongo.db.saved_games.insert_one(saved_game)
    return result.inserted_id

def get_user_saved_games(user_id):
    """Get a user's saved games."""
    if isinstance(user_id, str):
        try:
            user_id = ObjectId(user_id)
        except:
            return []
            
    return list(mongo.db.saved_games.find({"user_id": user_id}).sort("created_at", -1))

def get_saved_game_by_id(game_id):
    """Get a saved game by its ID."""
    try:
        if isinstance(game_id, str):
            game_id = ObjectId(game_id)
        return mongo.db.saved_games.find_one({"_id": game_id})
    except:
        return None

# Leaderboard functions
def get_top_players(min_games=5, limit=10):
    """Get the top players by win percentage (minimum games required)."""
    pipeline = [
        {"$match": {"games_played": {"$gte": min_games}}},
        {"$project": {
            "username": 1,
            "games_played": 1,
            "wins": 1,
            "losses": 1,
            "draws": 1,
            "win_percentage": {
                "$multiply": [
                    {"$divide": ["$wins", "$games_played"]},
                    100
                ]
            }
        }},
        {"$sort": {"win_percentage": -1}},
        {"$limit": limit}
    ]
    
    return list(mongo.db.users.aggregate(pipeline))
