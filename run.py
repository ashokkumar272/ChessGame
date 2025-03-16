#!/usr/bin/env python
"""
Chess Game with AI - Main entry point

This script starts the chess application with all its components:
- Chess game logic
- AI opponent
- Pygame UI
- Flask web server
"""

import sys
import os
import argparse
from threading import Thread
import json
import tempfile

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Chess Game with AI')
    parser.add_argument('--no-web', action='store_true', help='Disable web server')
    parser.add_argument('--no-ui', action='store_true', help='Disable Pygame UI')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--user-id', type=int, help='User ID for the Pygame UI to connect to')
    parser.add_argument('--token', type=str, help='Authentication token for the user')
    parser.add_argument('--difficulty', type=str, choices=['easy', 'medium', 'hard'], default='medium',
                        help='Difficulty level for the AI')
    parser.add_argument('--saved-game-id', type=int, help='ID of the saved game to load')
    parser.add_argument('--saved-game-fen', type=str, help='FEN of the saved game to load')
    return parser.parse_args()


def start_web_server(debug=False):
    """Start the Flask web server."""
    from chess_app.web.app import create_app
    app = create_app(debug=debug)
    app.run(host='0.0.0.0', port=5000, debug=debug)


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
    
    # Start web server in a separate thread if enabled
    if not args.no_web:
        web_thread = Thread(target=start_web_server, args=(args.debug,))
        web_thread.daemon = True
        web_thread.start()
        print("Web server started on http://localhost:5000")
    
    # Start Pygame UI if enabled
    if not args.no_ui:
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