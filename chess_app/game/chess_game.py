"""
Core chess game logic using python-chess library.
"""

import chess
import datetime
import json
import os
from typing import List, Optional, Dict


class ChessGame:
    """
    ChessGame class that handles the chess game state and logic.
    Uses python-chess library for game state representation and move validation.
    """
    
    def __init__(self, fen: str = None):
        """
        Initialize a new chess game, optionally from a FEN position.
        
        Args:
            fen: Optional Forsyth-Edwards Notation string to initialize the board
        """
        self.board = chess.Board(fen) if fen else chess.Board()
        self.move_history = []
        self.start_time = datetime.datetime.now()
        self.end_time = None
        self.game_result = None
        self.white_player = "Human"
        self.black_player = "AI"
        self.difficulty = "Medium"  # Default AI difficulty
    
    def make_move(self, move_uci: str) -> bool:
        """
        Make a move on the chess board using UCI notation.
        
        Args:
            move_uci: Move in UCI format (e.g., "e2e4")
            
        Returns:
            bool: True if the move was valid and made, False otherwise
        """
        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.move_history.append(move_uci)
                self._check_game_end()
                return True
            return False
        except ValueError:
            return False
    
    def _check_game_end(self) -> None:
        """
        Check if the game has ended and update the game result.
        """
        if self.board.is_checkmate():
            self.game_result = "checkmate"
            self.end_time = datetime.datetime.now()
        elif self.board.is_stalemate():
            self.game_result = "stalemate"
            self.end_time = datetime.datetime.now()
        elif self.board.is_insufficient_material():
            self.game_result = "insufficient_material"
            self.end_time = datetime.datetime.now()
        elif self.board.is_seventyfive_moves():
            self.game_result = "seventyfive_moves"
            self.end_time = datetime.datetime.now()
        elif self.board.is_fivefold_repetition():
            self.game_result = "fivefold_repetition"
            self.end_time = datetime.datetime.now()
    
    def get_legal_moves(self) -> List[str]:
        """
        Get all legal moves in the current position.
        
        Returns:
            List[str]: List of legal moves in UCI format
        """
        return [move.uci() for move in self.board.legal_moves]
    
    def is_game_over(self) -> bool:
        """
        Check if the game is over.
        
        Returns:
            bool: True if the game is over, False otherwise
        """
        return self.board.is_game_over()
    
    def get_winner(self) -> Optional[str]:
        """
        Get the winner of the game.
        
        Returns:
            str: "white", "black", or None if draw or game not over
        """
        if not self.is_game_over():
            return None
        
        outcome = self.board.outcome()
        if outcome is None:
            return None
        
        if outcome.winner is None:
            return None
        
        return "white" if outcome.winner else "black"
    
    def get_game_state(self) -> Dict:
        """
        Get the current game state.
        
        Returns:
            Dict: Dictionary containing the game state
        """
        winner = self.get_winner()
        winner_name = None
        if winner == "white":
            winner_name = self.white_player
        elif winner == "black":
            winner_name = self.black_player
        
        return {
            "fen": self.board.fen(),
            "moves": self.move_history,
            "is_game_over": self.is_game_over(),
            "result": self.game_result,
            "winner": winner_name,
            "turn": "white" if self.board.turn else "black",
            "white_player": self.white_player,
            "black_player": self.black_player,
            "difficulty": self.difficulty,
            "check": self.board.is_check(),
            "checkmate": self.board.is_checkmate(),
            "stalemate": self.board.is_stalemate(),
            "insufficient_material": self.board.is_insufficient_material(),
        }
    
    def save_game(self, filepath: str) -> None:
        """
        Save the game state to a file.
        
        Args:
            filepath: Path where to save the game state
        """
        game_data = {
            "fen": self.board.fen(),
            "moves": self.move_history,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "game_result": self.game_result,
            "white_player": self.white_player,
            "black_player": self.black_player,
            "difficulty": self.difficulty,
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(game_data, f, indent=4)
    
    @classmethod
    def load_game(cls, filepath: str) -> 'ChessGame':
        """
        Load a game from a file.
        
        Args:
            filepath: Path to the saved game file
            
        Returns:
            ChessGame: Loaded game instance
        """
        with open(filepath, 'r') as f:
            game_data = json.load(f)
        
        game = cls(fen=game_data["fen"])
        game.move_history = game_data["moves"]
        game.start_time = datetime.datetime.fromisoformat(game_data["start_time"])
        game.end_time = datetime.datetime.fromisoformat(game_data["end_time"]) if game_data["end_time"] else None
        game.game_result = game_data["game_result"]
        game.white_player = game_data["white_player"]
        game.black_player = game_data["black_player"]
        game.difficulty = game_data["difficulty"]
        
        return game 