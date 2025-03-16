"""
Pygame-based UI for the chess game.
"""

import pygame
import chess
import os
import sys
import json
import requests
import datetime
from typing import Tuple, Optional, List, Dict
from chess_app.game.chess_game import ChessGame
from chess_app.ai.chess_ai import ChessAI


class GameWindow:
    """
    Main game window class that handles the Pygame UI for the chess game.
    """
    
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    DARK_SQUARE = (118, 150, 86)  # Green
    LIGHT_SQUARE = (238, 238, 210)  # Cream
    HIGHLIGHT = (255, 255, 0, 128)  # Yellow with transparency
    MOVE_HIGHLIGHT = (100, 100, 255, 128)  # Blue with transparency
    
    # Board dimensions
    BOARD_SIZE = 512  # Total board size in pixels
    SQUARE_SIZE = BOARD_SIZE // 8  # Size of each square
    
    # Piece images directory
    PIECES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                             "assets", "pieces")
    
    def __init__(self, user_id=None, token=None, difficulty='medium', saved_game_id=None, saved_game_fen=None):
        """
        Initialize the game window and load resources.
        
        Args:
            user_id: Optional user ID to connect the game to a specific user account
            token: Authentication token for the user
            difficulty: AI difficulty level (easy, medium, hard)
            saved_game_id: Optional ID of a saved game to load
            saved_game_fen: Optional FEN position of a saved game to load
        """
        pygame.init()
        
        # Set up the display
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Chess Game with AI")
        
        # User authentication data
        self.user_id = user_id
        self.token = token
        self.username = None
        self.is_authenticated = False
        
        # Saved game data
        self.saved_game_id = saved_game_id
        self.saved_game_fen = saved_game_fen
        
        # Verify authentication and get user data if token is provided
        if user_id is not None and token is not None:
            self._verify_authentication()
        
        # Create assets directory if it doesn't exist
        self.assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                      "assets")
        os.makedirs(self.assets_dir, exist_ok=True)
        os.makedirs(self.PIECES_DIR, exist_ok=True)
        
        # Load piece images
        self.piece_images = self._load_piece_images()
        
        # Set the difficulty
        self.difficulty = difficulty.capitalize()
        
        # Initialize game state
        if saved_game_fen:
            self.chess_game = ChessGame(fen=saved_game_fen)
            self.message = "Saved game loaded"
        else:
            self.chess_game = ChessGame()
        
        self.ai = ChessAI(difficulty.lower())  # Set AI difficulty
        
        # UI state variables
        self.selected_square = None
        self.valid_moves = []
        self.is_player_turn = self.chess_game.board.turn == chess.WHITE  # White (human) starts
        self.is_game_over = self.chess_game.is_game_over()
        
        if self.is_game_over:
            winner = self.chess_game.get_winner()
            self._handle_game_end(winner)
        elif self.is_player_turn:
            self.message = "Your turn (White)"
        else:
            self.message = "AI is thinking..."
        
        self.game_start_time = datetime.datetime.now()
        
        # Font for text
        self.font = pygame.font.SysFont("Arial", 24)
        self.small_font = pygame.font.SysFont("Arial", 16)
        
        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()
        
        # If AI's turn (loaded a saved game where it's black's move), make the AI move
        if not self.is_player_turn and not self.is_game_over:
            # We'll make the AI move in the first frame of the game loop
            pass
    
    def _verify_authentication(self):
        """Verify user authentication with the server."""
        try:
            response = requests.post('http://localhost:5000/api/auth', 
                                    json={'token': self.token},
                                    headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                data = response.json()
                self.username = data.get('username')
                self.is_authenticated = True
                self.message = f"Welcome, {self.username}! Your turn (White)"
                print(f"Authenticated as user: {self.username} (ID: {self.user_id})")
            else:
                print(f"Authentication failed: {response.text}")
        except Exception as e:
            print(f"Error during authentication: {e}")
    
    def _load_piece_images(self) -> Dict:
        """
        Load chess piece images or create placeholders if images don't exist.
        
        Returns:
            Dict: Dictionary mapping piece symbols to their images
        """
        pieces = {}
        piece_symbols = ['p', 'n', 'b', 'r', 'q', 'k', 'P', 'N', 'B', 'R', 'Q', 'K']
        
        # Check if piece images exist, if not create placeholders
        for symbol in piece_symbols:
            image_path = os.path.join(self.PIECES_DIR, f"{symbol}.png")
            
            if os.path.exists(image_path):
                # Load the image if it exists
                image = pygame.image.load(image_path)
            else:
                # Create a placeholder image
                image = self._create_placeholder_piece(symbol)
                
                # Save the placeholder for future use
                pygame.image.save(image, image_path)
            
            # Scale the image to fit the square
            pieces[symbol] = pygame.transform.scale(image, (self.SQUARE_SIZE, self.SQUARE_SIZE))
        
        return pieces
    
    def _create_placeholder_piece(self, symbol: str) -> pygame.Surface:
        """
        Create a placeholder image for a chess piece.
        
        Args:
            symbol: Chess piece symbol (p, n, b, r, q, k, P, N, B, R, Q, K)
            
        Returns:
            pygame.Surface: Placeholder image for the piece
        """
        # Create a transparent surface
        image = pygame.Surface((100, 100), pygame.SRCALPHA)
        
        # Determine color based on case (uppercase = white, lowercase = black)
        color = self.WHITE if symbol.isupper() else self.BLACK
        
        # Draw a circle as the base
        pygame.draw.circle(image, color, (50, 50), 40)
        pygame.draw.circle(image, (128, 128, 128), (50, 50), 40, 2)
        
        # Add the symbol text
        font = pygame.font.SysFont("Arial", 60, bold=True)
        text = font.render(symbol.upper(), True, (255, 255, 255) if symbol.islower() else (0, 0, 0))
        text_rect = text.get_rect(center=(50, 50))
        image.blit(text, text_rect)
        
        return image
    
    def _draw(self):
        """Draw the game screen."""
        # Fill the background
        self.screen.fill((240, 240, 240))
        
        # Draw the chess board
        self._draw_board()
        
        # Draw the pieces
        self._draw_pieces()
        
        # Draw the UI elements
        self._draw_ui()
        
        # Update the display
        pygame.display.flip()
    
    def _draw_board(self):
        """Draw the chess board with square highlighting."""
        board_offset_x = (self.screen_width - self.BOARD_SIZE) // 2
        board_offset_y = (self.screen_height - self.BOARD_SIZE) // 2
        
        # Draw the squares
        for row in range(8):
            for col in range(8):
                x = board_offset_x + col * self.SQUARE_SIZE
                y = board_offset_y + row * self.SQUARE_SIZE
                
                # Determine square color
                color = self.LIGHT_SQUARE if (row + col) % 2 == 0 else self.DARK_SQUARE
                
                # Draw the square
                pygame.draw.rect(self.screen, color, (x, y, self.SQUARE_SIZE, self.SQUARE_SIZE))
                
                # Highlight selected square
                square = chess.square(col, 7 - row)  # Convert to chess.Square
                if square == self.selected_square:
                    highlight = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
                    highlight.fill(self.HIGHLIGHT)
                    self.screen.blit(highlight, (x, y))
                
                # Highlight valid moves
                if square in self.valid_moves:
                    highlight = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
                    highlight.fill(self.MOVE_HIGHLIGHT)
                    self.screen.blit(highlight, (x, y))
        
        # Draw the board border
        pygame.draw.rect(self.screen, self.BLACK, 
                         (board_offset_x, board_offset_y, self.BOARD_SIZE, self.BOARD_SIZE), 2)
        
        # Draw the coordinates
        for i in range(8):
            # Draw file labels (a-h)
            file_label = self.small_font.render(chess.FILE_NAMES[i], True, self.BLACK)
            x = board_offset_x + i * self.SQUARE_SIZE + self.SQUARE_SIZE // 2 - file_label.get_width() // 2
            y = board_offset_y + self.BOARD_SIZE + 5
            self.screen.blit(file_label, (x, y))
            
            # Draw rank labels (1-8)
            rank_label = self.small_font.render(str(8 - i), True, self.BLACK)
            x = board_offset_x - 15
            y = board_offset_y + i * self.SQUARE_SIZE + self.SQUARE_SIZE // 2 - rank_label.get_height() // 2
            self.screen.blit(rank_label, (x, y))
    
    def _draw_pieces(self):
        """Draw the chess pieces on the board."""
        board_offset_x = (self.screen_width - self.BOARD_SIZE) // 2
        board_offset_y = (self.screen_height - self.BOARD_SIZE) // 2
        
        for square in chess.SQUARES:
            piece = self.chess_game.board.piece_at(square)
            if piece:
                # Get the piece image
                symbol = piece.symbol()
                image = self.piece_images[symbol]
                
                # Calculate the position
                file_idx = chess.square_file(square)
                rank_idx = 7 - chess.square_rank(square)  # Flip the rank for display
                
                x = board_offset_x + file_idx * self.SQUARE_SIZE
                y = board_offset_y + rank_idx * self.SQUARE_SIZE
                
                # Draw the piece
                self.screen.blit(image, (x, y))
    
    def _draw_ui(self):
        """Draw the UI elements."""
        # Draw message text
        message_text = self.font.render(self.message, True, self.BLACK)
        message_rect = message_text.get_rect(center=(self.screen_width // 2, 30))
        self.screen.blit(message_text, message_rect)
        
        # Draw difficulty text
        difficulty_text = self.small_font.render(f"Difficulty: {self.difficulty}", True, self.BLACK)
        self.screen.blit(difficulty_text, (20, 20))
        
        # Draw user information if authenticated
        if self.is_authenticated:
            user_text = self.small_font.render(f"User: {self.username}", True, self.BLACK)
            self.screen.blit(user_text, (self.screen_width - user_text.get_width() - 20, 20))
        
        # Draw help text
        help_text = self.small_font.render("Press R to reset, 1-3 to change difficulty, S to save, L to load", True, self.BLACK)
        help_rect = help_text.get_rect(center=(self.screen_width // 2, self.screen_height - 20))
        self.screen.blit(help_text, help_rect)
    
    def _handle_mouse_click(self, pos: Tuple[int, int]):
        """
        Handle mouse clicks on the chess board.
        
        Args:
            pos: Mouse position (x, y)
        """
        # Calculate board offset
        board_offset_x = (self.screen_width - self.BOARD_SIZE) // 2
        board_offset_y = (self.screen_height - self.BOARD_SIZE) // 2
        
        # Check if the click is within the board
        if (board_offset_x <= pos[0] <= board_offset_x + self.BOARD_SIZE and
            board_offset_y <= pos[1] <= board_offset_y + self.BOARD_SIZE):
            
            # Calculate the square that was clicked
            file_idx = (pos[0] - board_offset_x) // self.SQUARE_SIZE
            rank_idx = (pos[1] - board_offset_y) // self.SQUARE_SIZE
            
            # Convert to chess.Square
            square = chess.square(file_idx, 7 - rank_idx)
            
            # If a square is already selected
            if self.selected_square is not None:
                # Check if the clicked square is a valid move
                if square in self.valid_moves:
                    # Make the move
                    move = chess.Move(self.selected_square, square)
                    
                    # Check for promotion
                    if self.chess_game.board.piece_at(self.selected_square).piece_type == chess.PAWN:
                        if 7 - rank_idx == 0:  # White pawn reaching the 8th rank
                            move = chess.Move(self.selected_square, square, promotion=chess.QUEEN)
                    
                    # Make the move in UCI format
                    self.chess_game.make_move(move.uci())
                    
                    # Reset selection
                    self.selected_square = None
                    self.valid_moves = []
                    
                    # Check if the game is over
                    if self.chess_game.is_game_over():
                        winner = self.chess_game.get_winner()
                        self._handle_game_end(winner)
                    else:
                        # Switch to AI's turn
                        self.is_player_turn = False
                        self.message = "AI is thinking..."
                else:
                    # If the clicked square is not a valid move, check if it has a piece of the player's color
                    piece = self.chess_game.board.piece_at(square)
                    if piece and piece.color == chess.WHITE:
                        # Select the new square
                        self.selected_square = square
                        self.valid_moves = self._get_valid_moves(square)
                    else:
                        # Deselect
                        self.selected_square = None
                        self.valid_moves = []
            else:
                # If no square is selected, select the clicked square if it has a piece of the player's color
                piece = self.chess_game.board.piece_at(square)
                if piece and piece.color == chess.WHITE:
                    self.selected_square = square
                    self.valid_moves = self._get_valid_moves(square)
    
    def _get_valid_moves(self, square: chess.Square) -> List[chess.Square]:
        """
        Get valid destination squares for a piece.
        
        Args:
            square: The square containing the piece to move
            
        Returns:
            List[chess.Square]: List of valid destination squares
        """
        valid_squares = []
        
        for move in self.chess_game.board.legal_moves:
            if move.from_square == square:
                valid_squares.append(move.to_square)
        
        return valid_squares
    
    def _make_ai_move(self):
        """Make a move for the AI."""
        # Get the best move from the AI
        ai_move = self.ai.get_best_move(self.chess_game.board)
        
        if ai_move:
            # Make the move
            self.chess_game.make_move(ai_move.uci())
            
            # Check if the game is over
            if self.chess_game.is_game_over():
                winner = self.chess_game.get_winner()
                self._handle_game_end(winner)
            else:
                # Switch back to player's turn
                self.is_player_turn = True
                self.message = "Your turn (White)"
    
    def _reset_game(self):
        """Reset the game to the initial state."""
        self.chess_game = ChessGame()
        self.selected_square = None
        self.valid_moves = []
        self.is_player_turn = True
        self.is_game_over = False
        self.message = "Your turn (White)"
    
    def _handle_game_end(self, winner):
        """
        Handle the end of a game, recording results to the user's account if authenticated.
        
        Args:
            winner: The winner of the game ('white', 'black', or None for draw)
        """
        self.is_game_over = True
        
        if winner == "white":
            self.message = "Game over! You win!"
            result = "win"
        elif winner == "black":
            self.message = "Game over! AI wins!"
            result = "loss"
        else:
            self.message = "Game over! It's a draw!"
            result = "draw"
            
        # Record the game to the user's account if authenticated
        if self.is_authenticated:
            self._record_game_to_account(result)
    
    def _record_game_to_account(self, result):
        """
        Record the completed game to the user's account.
        
        Args:
            result: Game result ('win', 'loss', 'draw')
        """
        try:
            # Prepare game data
            game_data = {
                'result': result,
                'difficulty': self.difficulty.lower(),
                'moves': self.chess_game.move_history,
                'final_fen': self.chess_game.board.fen(),
                'end_time': datetime.datetime.now().isoformat()
            }
            
            # Send the game data to the API
            response = requests.post('http://localhost:5000/api/record_game',
                                    json=game_data,
                                    headers={'Authorization': f'Bearer {self.token}', 
                                             'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                print(f"Game recorded successfully: {response.json()}")
            else:
                print(f"Failed to record game: {response.text}")
        except Exception as e:
            print(f"Error recording game: {e}")
    
    def _save_game(self):
        """Save the current game state."""
        if not self.is_authenticated:
            self.message = "You must be logged in to save games"
            return
            
        try:
            # Show a dialog to get the save name
            # In a real implementation, this would be a proper dialog
            # For now, we'll just use a simple name
            save_name = f"Game_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Prepare save data
            save_data = {
                'name': save_name,
                'fen': self.chess_game.board.fen(),
                'moves': self.chess_game.move_history,
                'difficulty': self.difficulty.lower()
            }
            
            # Send the save data to the API
            response = requests.post('http://localhost:5000/save_game',
                                    json=save_data,
                                    headers={'Authorization': f'Bearer {self.token}', 
                                             'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                self.message = f"Game saved as '{save_name}'"
                print(f"Game saved successfully: {response.json()}")
            else:
                self.message = "Failed to save game"
                print(f"Failed to save game: {response.text}")
        except Exception as e:
            self.message = "Error saving game"
            print(f"Error saving game: {e}")
    
    def run(self):
        """Main game loop."""
        running = True
        
        while running:
            # Handle AI move if it's the AI's turn
            if not self.is_player_turn and not self.is_game_over:
                self._make_ai_move()
            
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Left mouse button clicked
                    if not self.is_game_over and self.is_player_turn:
                        self._handle_mouse_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Reset the game
                        self._reset_game()
                    elif event.key == pygame.K_1:
                        # Set difficulty to easy
                        self.difficulty = "Easy"
                        self.ai.set_difficulty("easy")
                        self.message = f"Difficulty set to {self.difficulty}"
                    elif event.key == pygame.K_2:
                        # Set difficulty to medium
                        self.difficulty = "Medium"
                        self.ai.set_difficulty("medium")
                        self.message = f"Difficulty set to {self.difficulty}"
                    elif event.key == pygame.K_3:
                        # Set difficulty to hard
                        self.difficulty = "Hard"
                        self.ai.set_difficulty("hard")
                        self.message = f"Difficulty set to {self.difficulty}"
                    elif event.key == pygame.K_s:
                        # Save the game
                        self._save_game()
                    elif event.key == pygame.K_l:
                        # Load the game
                        if self.is_authenticated:
                            self.message = "Please load games from the website dashboard"
                        else:
                            self.message = "You must be logged in to load games"
            
            # Draw the game
            self._draw()
            
            # Cap the frame rate
            self.clock.tick(60)
        
        # Clean up resources before exiting
        pygame.quit()
        sys.exit() 