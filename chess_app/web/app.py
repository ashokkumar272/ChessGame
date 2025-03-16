"""
Flask web application for user management and game statistics.
"""

import os
import json
import subprocess
import secrets
import time
import sys
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from chess_app.db.models import db, User, Game, SavedGame
from chess_app.game.chess_game import ChessGame
from chess_app.web.forms import LoginForm, RegistrationForm, SaveGameForm

# Store tokens temporarily (in a real app, this would be in a database)
user_tokens = {}

def create_app(debug=False):
    """
    Create and configure the Flask application.
    
    Args:
        debug: Whether to run the app in debug mode
        
    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-chess-app')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///chess_app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = debug
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Create database tables
    with app.app_context():
        # Drop all tables and recreate when in debug mode
        if debug:
            db.drop_all()
            print("Dropped all database tables")
        db.create_all()
        print("Created database tables with updated schema")
    
    # Register routes
    
    @app.route('/')
    def index():
        """Home page route."""
        return render_template('index.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """User login route."""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard'))
            flash('Invalid username or password')
        
        return render_template('login.html', form=form)
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """User registration route."""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(username=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! You can now log in.')
            return redirect(url_for('login'))
        
        return render_template('register.html', form=form)
    
    @app.route('/logout')
    @login_required
    def logout():
        """User logout route."""
        logout_user()
        return redirect(url_for('index'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """User dashboard route."""
        # Get user's game statistics
        stats = {
            'games_played': current_user.games_played,
            'wins': current_user.wins,
            'losses': current_user.losses,
            'draws': current_user.draws,
            'win_percentage': current_user.get_win_percentage()
        }
        
        # Get recent games
        recent_games = Game.query.filter_by(user_id=current_user.id).order_by(Game.end_time.desc()).limit(5).all()
        
        # Get saved games
        saved_games = SavedGame.query.filter_by(user_id=current_user.id).order_by(SavedGame.created_at.desc()).all()
        
        return render_template('dashboard.html', stats=stats, recent_games=recent_games, saved_games=saved_games)
    
    @app.route('/game_history')
    @login_required
    def game_history():
        """View game history route."""
        games = Game.query.filter_by(user_id=current_user.id).order_by(Game.end_time.desc()).all()
        return render_template('game_history.html', games=games)
    
    @app.route('/game/<int:game_id>')
    @login_required
    def view_game(game_id):
        """View a specific game route."""
        game = Game.query.get_or_404(game_id)
        
        # Check if the game belongs to the current user
        if game.user_id != current_user.id:
            flash('You do not have permission to view this game.')
            return redirect(url_for('game_history'))
        
        # Parse the moves from JSON
        moves = json.loads(game.moves) if game.moves else []
        
        return render_template('view_game.html', game=game, moves=moves)
    
    @app.route('/save_game', methods=['POST'])
    @login_required
    def save_game():
        """API endpoint to save a game state."""
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        form = SaveGameForm(data=data)
        if form.validate():
            saved_game = SavedGame(
                user_id=current_user.id,
                name=form.name.data,
                fen=form.fen.data,
                moves=json.dumps(form.moves.data),
                difficulty=form.difficulty.data
            )
            db.session.add(saved_game)
            db.session.commit()
            return jsonify({'success': True, 'id': saved_game.id})
        
        return jsonify({'error': 'Invalid data', 'errors': form.errors}), 400
    
    @app.route('/load_game/<int:game_id>')
    @login_required
    def load_game(game_id):
        """Load a saved game route."""
        saved_game = SavedGame.query.get_or_404(game_id)
        
        # Check if the game belongs to the current user
        if saved_game.user_id != current_user.id:
            flash('You do not have permission to load this game.')
            return redirect(url_for('dashboard'))
        
        # Redirect to the game page with the saved game data
        return redirect(url_for('play', saved_game_id=game_id))
    
    @app.route('/play')
    @login_required
    def play():
        """Play chess route."""
        saved_game_id = request.args.get('saved_game_id')
        saved_game = None
        
        if saved_game_id:
            saved_game = SavedGame.query.get(saved_game_id)
            
            # Check if the game belongs to the current user
            if saved_game and saved_game.user_id != current_user.id:
                flash('You do not have permission to load this game.')
                saved_game = None
        
        return render_template('play.html', saved_game=saved_game)
    
    @app.route('/launch_game', methods=['POST'])
    @login_required
    def launch_game():
        """Launch the Pygame chess game with the current user's credentials."""
        # Generate a token for the user
        token = secrets.token_hex(16)
        user_tokens[token] = {
            'user_id': current_user.id,
            'created_at': time.time()
        }
        
        # Get the difficulty level from the form
        difficulty = request.form.get('difficulty', 'medium')
        
        # Check if a saved game ID was provided
        saved_game_id = request.form.get('saved_game_id')
        saved_game_params = []
        
        if saved_game_id:
            saved_game = SavedGame.query.get(saved_game_id)
            if saved_game and saved_game.user_id == current_user.id:
                # Add saved game parameters
                saved_game_params = [
                    '--saved-game-id', saved_game_id,
                    '--saved-game-fen', saved_game.fen
                ]
        
        # Get the main script path
        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'run.py')
        
        try:
            # Launch the game with the user's credentials
            subprocess.Popen([
                sys.executable,
                script_path,
                '--no-web',
                '--user-id', str(current_user.id),
                '--token', token,
                '--difficulty', difficulty.lower()
            ] + saved_game_params)
            
            return jsonify({'success': True, 'message': 'Game launched successfully'})
        except Exception as e:
            return jsonify({'error': f'Failed to launch game: {str(e)}'}), 500
    
    @app.route('/api/record_game', methods=['POST'])
    @login_required
    def record_game():
        """API endpoint to record a completed game."""
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['result', 'difficulty', 'moves', 'final_fen']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create a new game record
        game = Game(
            user_id=current_user.id,
            result=data['result'],
            difficulty=data['difficulty'],
            moves=json.dumps(data['moves']),
            final_fen=data['final_fen'],
            end_time=data.get('end_time')
        )
        
        # Update user statistics
        current_user.update_stats(data['result'])
        
        # Save to database
        db.session.add(game)
        db.session.commit()
        
        return jsonify({'success': True, 'id': game.id})
    
    @app.route('/api/auth', methods=['POST'])
    def authenticate_token():
        """API endpoint to validate auth tokens."""
        data = request.json
        
        if not data or 'token' not in data:
            return jsonify({'error': 'No token provided'}), 400
            
        token = data['token']
        
        if token in user_tokens:
            token_data = user_tokens[token]
            # Check if token is not expired (30 minutes validity)
            if time.time() - token_data['created_at'] < 1800:
                user = User.query.get(token_data['user_id'])
                if user:
                    return jsonify({'success': True, 'user_id': user.id, 'username': user.username})
        
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    @app.route('/leaderboard')
    def leaderboard():
        """Leaderboard route."""
        # Get top players by win percentage (minimum 5 games)
        top_players = User.query.filter(User.games_played >= 5).order_by((User.wins * 100 / User.games_played).desc()).limit(10).all()
        
        return render_template('leaderboard.html', top_players=top_players)
    
    # Create a test user if none exists (for development)
    with app.app_context():
        if not User.query.first() and debug:
            test_user = User(username='test')
            test_user.set_password('password')
            db.session.add(test_user)
            db.session.commit()
            print("Created test user: username='test', password='password'")
    
    return app 