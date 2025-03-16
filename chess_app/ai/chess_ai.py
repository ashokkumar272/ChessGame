"""
Chess AI implementation using python-chess with different difficulty levels.
"""

import chess
import random
from typing import Optional, List, Dict, Tuple
import time

class ChessAI:
    """
    Chess AI class that provides different difficulty levels for the computer opponent.
    Uses minimax algorithm with alpha-beta pruning for harder difficulty levels.
    """
    
    PIECE_VALUES = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }
    
    # Piece-square tables for positional evaluation
    PAWN_TABLE = [
        0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5,  5, 10, 25, 25, 10,  5,  5,
        0,  0,  0, 20, 20,  0,  0,  0,
        5, -5,-10,  0,  0,-10, -5,  5,
        5, 10, 10,-20,-20, 10, 10,  5,
        0,  0,  0,  0,  0,  0,  0,  0
    ]
    
    KNIGHT_TABLE = [
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50
    ]
    
    BISHOP_TABLE = [
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  5,  5,  5,  5,  5,  5,-10,
        -10,  0,  5,  0,  0,  5,  0,-10,
        -20,-10,-10,-10,-10,-10,-10,-20
    ]
    
    ROOK_TABLE = [
        0,  0,  0,  0,  0,  0,  0,  0,
        5, 10, 10, 10, 10, 10, 10,  5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        0,  0,  0,  5,  5,  0,  0,  0
    ]
    
    QUEEN_TABLE = [
        -20,-10,-10, -5, -5,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5,  5,  5,  5,  0,-10,
        -5,  0,  5,  5,  5,  5,  0, -5,
        0,  0,  5,  5,  5,  5,  0, -5,
        -10,  5,  5,  5,  5,  5,  0,-10,
        -10,  0,  5,  0,  0,  0,  0,-10,
        -20,-10,-10, -5, -5,-10,-10,-20
    ]
    
    KING_MIDDLE_GAME_TABLE = [
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -20,-30,-30,-40,-40,-30,-30,-20,
        -10,-20,-20,-20,-20,-20,-20,-10,
        20, 20,  0,  0,  0,  0, 20, 20,
        20, 30, 10,  0,  0, 10, 30, 20
    ]
    
    KING_END_GAME_TABLE = [
        -50,-40,-30,-20,-20,-30,-40,-50,
        -30,-20,-10,  0,  0,-10,-20,-30,
        -30,-10, 20, 30, 30, 20,-10,-30,
        -30,-10, 30, 40, 40, 30,-10,-30,
        -30,-10, 30, 40, 40, 30,-10,-30,
        -30,-10, 20, 30, 30, 20,-10,-30,
        -30,-30,  0,  0,  0,  0,-30,-30,
        -50,-30,-30,-30,-30,-30,-30,-50
    ]
    
    def __init__(self, difficulty: str = "medium"):
        """
        Initialize the AI with a specific difficulty level.
        
        Args:
            difficulty: Difficulty level of the AI ("easy", "medium", "hard")
        """
        self.set_difficulty(difficulty)
    
    def set_difficulty(self, difficulty: str) -> None:
        """
        Set the difficulty level of the AI.
        
        Args:
            difficulty: Difficulty level ("easy", "medium", "hard")
        """
        difficulty = difficulty.lower()
        if difficulty not in ["easy", "medium", "hard"]:
            difficulty = "medium"
        
        self.difficulty = difficulty
        
        # Configure search depth based on difficulty
        if difficulty == "easy":
            self.search_depth = 1
            self.use_opening_book = False
            self.use_positional = False
        elif difficulty == "medium":
            self.search_depth = 2
            self.use_opening_book = True
            self.use_positional = True
        else:  # hard
            self.search_depth = 3
            self.use_opening_book = True
            self.use_positional = True
    
    def get_best_move(self, board: chess.Board) -> Optional[chess.Move]:
        """
        Get the best move for the current position based on the AI difficulty.
        
        Args:
            board: Current chess board position
            
        Returns:
            Optional[chess.Move]: Best move according to the AI
        """
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        
        # Easy difficulty: Random move with basic capture prioritization
        if self.difficulty == "easy":
            return self._get_easy_move(board, legal_moves)
        
        # Medium and Hard: Use minimax with alpha-beta pruning
        best_move = None
        best_value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        # Add some randomness to make the AI less predictable
        random.shuffle(legal_moves)
        
        # Iterative deepening for better move ordering
        for depth in range(1, self.search_depth + 1):
            current_best_move = None
            current_best_value = float('-inf')
            
            for move in legal_moves:
                board.push(move)
                # Call minimax for the opponent's turn (minimizing player)
                value = self._minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                
                if value > current_best_value:
                    current_best_value = value
                    current_best_move = move
                    
                alpha = max(alpha, current_best_value)
            
            # Update the overall best move after each iteration
            if current_best_move:
                best_move = current_best_move
                best_value = current_best_value
        
        return best_move or random.choice(legal_moves)
    
    def _get_easy_move(self, board: chess.Board, legal_moves: List[chess.Move]) -> chess.Move:
        """
        Get a move for easy difficulty - prioritizes captures and checks but with randomness.
        
        Args:
            board: Current chess board
            legal_moves: List of legal moves
            
        Returns:
            chess.Move: Selected move
        """
        # 10% chance of just making a completely random move
        if random.random() < 0.1:
            return random.choice(legal_moves)
        
        # Check if any move is a capture, and if so prioritize it
        capturing_moves = [move for move in legal_moves if board.is_capture(move)]
        if capturing_moves:
            # 80% chance of choosing a capture when available
            if random.random() < 0.8:
                return random.choice(capturing_moves)
        
        # Check if any move gives check
        checking_moves = [move for move in legal_moves if board.gives_check(move)]
        if checking_moves:
            # 70% chance of choosing a checking move when available
            if random.random() < 0.7:
                return random.choice(checking_moves)
        
        # Otherwise choose a random move
        return random.choice(legal_moves)
    
    def _minimax(self, board: chess.Board, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
        """
        Minimax algorithm with alpha-beta pruning for chess move evaluation.
        
        Args:
            board: Current chess board position
            depth: Current search depth
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            maximizing: Whether this is a maximizing or minimizing player
            
        Returns:
            float: Evaluation score of the position
        """
        if depth == 0 or board.is_game_over():
            return self._evaluate_position(board)
        
        if maximizing:
            value = float('-inf')
            for move in board.legal_moves:
                board.push(move)
                value = max(value, self._minimax(board, depth - 1, alpha, beta, False))
                board.pop()
                alpha = max(alpha, value)
                if alpha >= beta:
                    break  # Beta cutoff
            return value
        else:
            value = float('inf')
            for move in board.legal_moves:
                board.push(move)
                value = min(value, self._minimax(board, depth - 1, alpha, beta, True))
                board.pop()
                beta = min(beta, value)
                if beta <= alpha:
                    break  # Alpha cutoff
            return value
    
    def _evaluate_position(self, board: chess.Board) -> float:
        """
        Evaluate the current board position.
        
        Args:
            board: Current chess board position
            
        Returns:
            float: Evaluation score (positive for white advantage, negative for black)
        """
        if board.is_checkmate():
            # Return a high value for checkmate, considering whose turn it is
            return -10000 if board.turn else 10000
        
        if board.is_stalemate() or board.is_insufficient_material():
            return 0  # Draw
        
        # Material evaluation
        material_score = self._evaluate_material(board)
        
        # Positional evaluation (only for medium and hard difficulty)
        positional_score = 0
        if self.use_positional:
            positional_score = self._evaluate_position_score(board)
        
        # Mobility evaluation - count number of legal moves
        mobility_score = 0
        if board.turn:  # White's turn
            mobility_score = len(list(board.legal_moves)) * 5
        else:  # Black's turn
            mobility_score = -len(list(board.legal_moves)) * 5
        
        # King safety (simplified)
        king_safety = self._evaluate_king_safety(board)
        
        # Combine all evaluation components
        total_score = material_score + positional_score + mobility_score + king_safety
        
        # Return score from white's perspective
        return total_score if board.turn else -total_score
    
    def _evaluate_material(self, board: chess.Board) -> float:
        """
        Evaluate the material balance on the board.
        
        Args:
            board: Current chess board
            
        Returns:
            float: Material evaluation score
        """
        score = 0
        
        # Count material for each piece type
        for piece_type in chess.PIECE_TYPES:
            score += len(board.pieces(piece_type, chess.WHITE)) * self.PIECE_VALUES[piece_type]
            score -= len(board.pieces(piece_type, chess.BLACK)) * self.PIECE_VALUES[piece_type]
        
        return score
    
    def _evaluate_position_score(self, board: chess.Board) -> float:
        """
        Evaluate the positional quality of the pieces.
        
        Args:
            board: Current chess board
            
        Returns:
            float: Positional evaluation score
        """
        score = 0
        
        # Determine game phase (middle or endgame)
        is_endgame = self._is_endgame(board)
        
        # Evaluate piece positions using piece-square tables
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is None:
                continue
            
            # Get the appropriate index for the piece-square table
            # For black pieces, we need to flip the square index
            square_idx = square
            if not piece.color:
                square_idx = chess.square_mirror(square)
            
            if piece.piece_type == chess.PAWN:
                value = self.PAWN_TABLE[square_idx]
            elif piece.piece_type == chess.KNIGHT:
                value = self.KNIGHT_TABLE[square_idx]
            elif piece.piece_type == chess.BISHOP:
                value = self.BISHOP_TABLE[square_idx]
            elif piece.piece_type == chess.ROOK:
                value = self.ROOK_TABLE[square_idx]
            elif piece.piece_type == chess.QUEEN:
                value = self.QUEEN_TABLE[square_idx]
            elif piece.piece_type == chess.KING:
                if is_endgame:
                    value = self.KING_END_GAME_TABLE[square_idx]
                else:
                    value = self.KING_MIDDLE_GAME_TABLE[square_idx]
            
            # Add or subtract the positional value based on piece color
            if piece.color:  # White
                score += value
            else:  # Black
                score -= value
        
        return score
    
    def _evaluate_king_safety(self, board: chess.Board) -> float:
        """
        Evaluate the safety of both kings.
        
        Args:
            board: Current chess board
            
        Returns:
            float: King safety evaluation score
        """
        score = 0
        
        # Count the defenders around each king
        white_king_square = board.king(chess.WHITE)
        black_king_square = board.king(chess.BLACK)
        
        # Skip if kings are not on the board (shouldn't happen in a valid game)
        if white_king_square is None or black_king_square is None:
            return 0
        
        # Get adjacent squares to the kings
        white_king_zone = list(chess.SquareSet(chess.BB_KING_ATTACKS[white_king_square]))
        black_king_zone = list(chess.SquareSet(chess.BB_KING_ATTACKS[black_king_square]))
        
        # Count defenders in king zones (simplified)
        white_defenders = 0
        black_defenders = 0
        
        for square in white_king_zone:
            piece = board.piece_at(square)
            if piece and piece.color == chess.WHITE:
                white_defenders += 1
        
        for square in black_king_zone:
            piece = board.piece_at(square)
            if piece and piece.color == chess.BLACK:
                black_defenders += 1
        
        # Penalize exposed kings and reward defended kings
        score += white_defenders * 10
        score -= black_defenders * 10
        
        return score
    
    def _is_endgame(self, board: chess.Board) -> bool:
        """
        Determine if the position is in the endgame phase.
        
        Args:
            board: Current chess board
            
        Returns:
            bool: True if it's an endgame position, False otherwise
        """
        # Simplified endgame detection: if queens are off the board
        # or if both sides have less than 13 points in non-pawn material
        white_queens = len(board.pieces(chess.QUEEN, chess.WHITE))
        black_queens = len(board.pieces(chess.QUEEN, chess.BLACK))
        
        if white_queens == 0 and black_queens == 0:
            return True
        
        # Count material excluding pawns and kings
        white_material = (len(board.pieces(chess.KNIGHT, chess.WHITE)) * 3 +
                        len(board.pieces(chess.BISHOP, chess.WHITE)) * 3 +
                        len(board.pieces(chess.ROOK, chess.WHITE)) * 5 +
                        len(board.pieces(chess.QUEEN, chess.WHITE)) * 9)
        
        black_material = (len(board.pieces(chess.KNIGHT, chess.BLACK)) * 3 +
                         len(board.pieces(chess.BISHOP, chess.BLACK)) * 3 +
                         len(board.pieces(chess.ROOK, chess.BLACK)) * 5 +
                         len(board.pieces(chess.QUEEN, chess.BLACK)) * 9)
        
        return white_material < 13 and black_material < 13 