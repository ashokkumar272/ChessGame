#!/usr/bin/env python
"""
Chess Game with AI - Main entry point

This script starts the chess application with all its components:
- Chess game logic
- AI opponent
- Pygame UI
- Flask web server with MongoDB
"""

import sys
import os
import argparse
from threading import Thread
import json
import tempfile
import logging

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Chess Game with AI')
    parser.add_argument('--no-web', action='store_true', help='Disable web server and run standalone game')
    parser.add_argument('--user-id', type=str, help='User ID for the Pygame UI to connect to')
    parser.add_argument('--token', type=str, help='Authentication token for the user')
    parser.add_argument('--difficulty', type=str, choices=['easy', 'medium', 'hard'], default='medium',
                        help='Difficulty level for the AI')
    parser.add_argument('--saved-game-id', type=str, help='ID of the saved game to load')
    parser.add_argument('--saved-game-fen', type=str, help='FEN of the saved game to load')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--mongo-uri', type=str, help='MongoDB connection URI')
    parser.add_argument('--quiet', action='store_true', help='Show minimal server output')
    return parser.parse_args()


def start_web_server(debug=False, mongo_uri=None):
    """Start the Flask web server."""
    if mongo_uri:
        os.environ['MONGO_URI'] = mongo_uri
    
    # Disable Flask's default logging
    if not debug:
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
    
    from chess_app.web.app import create_app
    app = create_app(debug=debug)
    
    # Check database connection
    try:
        with app.app_context():
            from chess_app.db.mongo_db import mongo
            mongo.db.command('ping')
            db_connected = True
    except Exception as e:
        db_connected = False
        if debug:
            print(f"Database connection error: {e}")
    
    # Print simplified output
    host = '0.0.0.0'
    port = 5000
    print("\n=== Chess Game with AI ===")
    print(f"Server running at http://localhost:{port}")
    if db_connected:
        print("Database connection: OK")
    else:
        print("Database connection: FAILED")
    print("Press Ctrl+C to quit")
    print("=" * 25)
    
    # Run the Flask app with minimal output
    app.run(host=host, port=port, debug=debug, use_reloader=False)


def start_game_ui(user_id=None, token=None, difficulty='medium', saved_game_id=None, saved_game_fen=None):
    """
    Start the Pygame UI.
    
    Args:
        user_id: Optional user ID to connect the game to a specific user account
        token: Authentication token for the user
        difficulty: AI difficulty level (easy, medium, hard)
        saved_game_id: Optional ID of a saved game to load
        saved_game_fen: Optional FEN position of a saved game to load
    """
    from chess_app.ui.game_window import GameWindow
    game_window = GameWindow(
        user_id=user_id, 
        token=token,
        difficulty=difficulty,
        saved_game_id=saved_game_id,
        saved_game_fen=saved_game_fen
    )
    game_window.run()


def main():
    """Main function to start the application."""
    args = parse_args()
    
    # Set MongoDB URI if provided
    mongo_uri = args.mongo_uri
    
    # Start web server in a separate thread if enabled
    if not args.no_web:
        web_thread = Thread(target=start_web_server, args=(args.debug, mongo_uri))
        web_thread.daemon = True
        web_thread.start()
    
    # Only start Pygame UI if explicitly requested with specific arguments
    # or when --no-web is used (standalone mode)
    if args.no_web or (args.user_id is not None and args.token is not None):
        start_game_ui(
            user_id=args.user_id, 
            token=args.token,
            difficulty=args.difficulty,
            saved_game_id=args.saved_game_id,
            saved_game_fen=args.saved_game_fen
        )
    elif not args.no_web:
        # If UI is disabled but web is enabled, keep the script running
        try:
            web_thread.join()
        except KeyboardInterrupt:
            print("\nShutting down...")
            sys.exit(0)


if __name__ == "__main__":
    main()