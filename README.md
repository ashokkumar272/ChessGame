# Chess Game with AI

A full-featured chess application that allows users to play against AI opponents with multiple difficulty levels.

## Features

- Play chess against AI opponents
- Multiple AI difficulty levels (Easy, Medium, Hard)
- User authentication system
- Track game statistics (wins, losses, draws)
- Review previous games
- Save game states for future reference
- Intuitive Pygame-based UI
- Web interface with game history and replay functionality

## Project Structure

- `chess_app/` - Main application package
  - `game/` - Chess game logic using python-chess
  - `ai/` - AI opponent implementation
  - `ui/` - Pygame-based user interface
  - `web/` - Flask web application for user management and statistics
  - `db/` - Database models and interactions for MongoDB
- `assets/` - Game assets (piece images, etc.)

## Requirements

- Python 3.8+
- MongoDB running locally (default: mongodb://localhost:27017/chess_app)

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Make sure MongoDB is installed and running

## Running the Game

There are two main components to this application:

### 1. Pygame Chess Interface

To start the game with the Pygame interface:

```
python run.py
```

This will launch the chess game window where you can play against the AI.

### 2. Web Interface

To start only the web interface (for user management, statistics, etc.):

```
python run.py --no-web
```

This will start the Flask web server. You can then access the web interface at http://localhost:5000.

### Command Line Options

- `--no-web`: Disable the web server and run standalone game
- `--user-id`: User ID for the Pygame UI to connect to
- `--token`: Authentication token for the user
- `--difficulty`: Difficulty level for the AI (easy, medium, hard)
- `--saved-game-id`: ID of the saved game to load
- `--saved-game-fen`: FEN of the saved game to load
- `--debug`: Enable debug mode
- `--mongo-uri`: MongoDB connection URI
- `--quiet`: Show minimal server output

## Playing the Game

1. Use the mouse to select and move pieces on the board
2. Press keys to access different features:
   - `R` - Reset the game
   - `1` - Set difficulty to Easy
   - `2` - Set difficulty to Medium
   - `3` - Set difficulty to Hard
   - `S` - Save the current game
   - `L` - Load a saved game

## Web Interface Features

- User registration and login
- Dashboard with game statistics
- Game history and replay
- Leaderboard
- Save and load games
- Launch Pygame interface directly from the browser

## Development

To run tests:
```
pytest
```

## Technologies Used

- Python 3.8+
- python-chess - Chess logic library
- Pygame - Game UI
- Flask - Web backend
- Flask-Login - User authentication
- PyMongo/MongoDB - Database
- Bootstrap - Frontend styling

## License

This project is open source and available under the MIT License.