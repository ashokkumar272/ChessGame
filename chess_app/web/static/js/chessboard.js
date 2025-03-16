/**
 * Chessboard JavaScript for the web interface
 * This is a simplified version for demonstration purposes.
 * The actual gameplay happens in the Pygame interface.
 */

class Chessboard {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Container with ID "${containerId}" not found.`);
            return;
        }
        
        this.options = Object.assign({
            showCoordinates: true,
            draggable: true,
            orientation: 'white',
            position: 'start'
        }, options);
        
        this.selectedSquare = null;
        this.highlightedSquares = [];
        this.pieces = {};
        
        this._createBoard();
        this._setupInitialPosition();
        this._setupEventListeners();
    }
    
    _createBoard() {
        // Create the chessboard element
        this.boardElement = document.createElement('div');
        this.boardElement.className = 'chessboard';
        this.container.appendChild(this.boardElement);
        
        // Create squares
        const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
        const ranks = ['8', '7', '6', '5', '4', '3', '2', '1'];
        
        for (let rankIndex = 0; rankIndex < 8; rankIndex++) {
            for (let fileIndex = 0; fileIndex < 8; fileIndex++) {
                const squareElement = document.createElement('div');
                const isLight = (rankIndex + fileIndex) % 2 === 0;
                squareElement.className = `square ${isLight ? 'light' : 'dark'}`;
                
                const file = files[fileIndex];
                const rank = ranks[rankIndex];
                const squareName = file + rank;
                squareElement.dataset.square = squareName;
                
                // Add coordinates if enabled
                if (this.options.showCoordinates) {
                    if (fileIndex === 0) {
                        const rankLabel = document.createElement('span');
                        rankLabel.className = 'rank-label';
                        rankLabel.textContent = rank;
                        squareElement.appendChild(rankLabel);
                    }
                    
                    if (rankIndex === 7) {
                        const fileLabel = document.createElement('span');
                        fileLabel.className = 'file-label';
                        fileLabel.textContent = file;
                        squareElement.appendChild(fileLabel);
                    }
                }
                
                this.boardElement.appendChild(squareElement);
            }
        }
    }
    
    _setupInitialPosition() {
        if (this.options.position === 'start') {
            // Set up the initial position
            const initialPosition = {
                'a8': 'br', 'b8': 'bn', 'c8': 'bb', 'd8': 'bq', 'e8': 'bk', 'f8': 'bb', 'g8': 'bn', 'h8': 'br',
                'a7': 'bp', 'b7': 'bp', 'c7': 'bp', 'd7': 'bp', 'e7': 'bp', 'f7': 'bp', 'g7': 'bp', 'h7': 'bp',
                'a2': 'wp', 'b2': 'wp', 'c2': 'wp', 'd2': 'wp', 'e2': 'wp', 'f2': 'wp', 'g2': 'wp', 'h2': 'wp',
                'a1': 'wr', 'b1': 'wn', 'c1': 'wb', 'd1': 'wq', 'e1': 'wk', 'f1': 'wb', 'g1': 'wn', 'h1': 'wr'
            };
            
            for (const [square, piece] of Object.entries(initialPosition)) {
                this.addPiece(square, piece);
            }
        } else if (typeof this.options.position === 'object') {
            // Set up a custom position
            for (const [square, piece] of Object.entries(this.options.position)) {
                this.addPiece(square, piece);
            }
        }
    }
    
    _setupEventListeners() {
        if (this.options.draggable) {
            this.boardElement.addEventListener('click', (event) => {
                const squareElement = event.target.closest('.square');
                if (!squareElement) return;
                
                const square = squareElement.dataset.square;
                this._handleSquareClick(square);
            });
        }
    }
    
    _handleSquareClick(square) {
        // If a square is already selected
        if (this.selectedSquare) {
            // If the same square is clicked again, deselect it
            if (this.selectedSquare === square) {
                this.clearHighlights();
                this.selectedSquare = null;
                return;
            }
            
            // If a different square is clicked, try to move the piece
            const fromSquare = this.selectedSquare;
            const toSquare = square;
            
            // Check if the move is valid (simplified for demo)
            if (this.highlightedSquares.includes(toSquare)) {
                this.movePiece(fromSquare, toSquare);
            } else {
                // If the clicked square has a piece of the same color, select it instead
                const piece = this.pieces[square];
                if (piece && this._isPieceOwnedByCurrentPlayer(piece)) {
                    this.clearHighlights();
                    this.selectedSquare = square;
                    this.highlightSquare(square);
                    this._highlightLegalMoves(square, piece);
                } else {
                    // Otherwise, clear selection
                    this.clearHighlights();
                    this.selectedSquare = null;
                }
            }
        } else {
            // If no square is selected, select the clicked square if it has a piece
            const piece = this.pieces[square];
            if (piece && this._isPieceOwnedByCurrentPlayer(piece)) {
                this.selectedSquare = square;
                this.highlightSquare(square);
                this._highlightLegalMoves(square, piece);
            }
        }
    }
    
    _isPieceOwnedByCurrentPlayer(piece) {
        // In a real implementation, this would check if the piece belongs to the current player
        // For demo purposes, we'll just return true
        return true;
    }
    
    _highlightLegalMoves(square, piece) {
        // In a real implementation, this would calculate legal moves based on the piece and position
        // For demo purposes, we'll just highlight some arbitrary squares
        const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
        const ranks = ['1', '2', '3', '4', '5', '6', '7', '8'];
        
        const [file, rank] = square.split('');
        const fileIndex = files.indexOf(file);
        const rankIndex = ranks.indexOf(rank);
        
        // Highlight some squares based on piece type (simplified)
        if (piece[1] === 'p') {  // Pawn
            const direction = piece[0] === 'w' ? 1 : -1;
            const newRank = ranks[rankIndex + direction];
            if (newRank) {
                this.highlightMoveSquare(file + newRank);
            }
        } else if (piece[1] === 'r') {  // Rook
            // Highlight some squares in the same file and rank
            for (let i = 1; i <= 2; i++) {
                if (fileIndex + i < 8) this.highlightMoveSquare(files[fileIndex + i] + rank);
                if (rankIndex + i < 8) this.highlightMoveSquare(file + ranks[rankIndex + i]);
            }
        } else if (piece[1] === 'n') {  // Knight
            // Highlight some knight moves
            if (fileIndex + 2 < 8 && rankIndex + 1 < 8) this.highlightMoveSquare(files[fileIndex + 2] + ranks[rankIndex + 1]);
            if (fileIndex + 1 < 8 && rankIndex + 2 < 8) this.highlightMoveSquare(files[fileIndex + 1] + ranks[rankIndex + 2]);
        } else {  // Other pieces
            // Just highlight some adjacent squares
            if (fileIndex + 1 < 8) this.highlightMoveSquare(files[fileIndex + 1] + rank);
            if (rankIndex + 1 < 8) this.highlightMoveSquare(file + ranks[rankIndex + 1]);
            if (fileIndex + 1 < 8 && rankIndex + 1 < 8) this.highlightMoveSquare(files[fileIndex + 1] + ranks[rankIndex + 1]);
        }
    }
    
    addPiece(square, piece) {
        const squareElement = this.boardElement.querySelector(`[data-square="${square}"]`);
        if (!squareElement) return;
        
        // Remove any existing piece
        this.removePiece(square);
        
        // Create the piece element
        const pieceElement = document.createElement('div');
        pieceElement.className = 'piece';
        pieceElement.dataset.piece = piece;
        
        // Set the piece image or text representation
        const color = piece[0] === 'w' ? 'white' : 'black';
        let pieceName;
        switch (piece[1]) {
            case 'p': pieceName = 'pawn'; break;
            case 'r': pieceName = 'rook'; break;
            case 'n': pieceName = 'knight'; break;
            case 'b': pieceName = 'bishop'; break;
            case 'q': pieceName = 'queen'; break;
            case 'k': pieceName = 'king'; break;
        }
        
        // For demo purposes, we'll just use text
        pieceElement.textContent = piece;
        pieceElement.style.backgroundColor = color === 'white' ? '#fff' : '#000';
        pieceElement.style.color = color === 'white' ? '#000' : '#fff';
        pieceElement.style.borderRadius = '50%';
        pieceElement.style.display = 'flex';
        pieceElement.style.justifyContent = 'center';
        pieceElement.style.alignItems = 'center';
        pieceElement.style.fontWeight = 'bold';
        
        squareElement.appendChild(pieceElement);
        this.pieces[square] = piece;
    }
    
    removePiece(square) {
        const squareElement = this.boardElement.querySelector(`[data-square="${square}"]`);
        if (!squareElement) return;
        
        const pieceElement = squareElement.querySelector('.piece');
        if (pieceElement) {
            squareElement.removeChild(pieceElement);
        }
        
        delete this.pieces[square];
    }
    
    movePiece(fromSquare, toSquare) {
        const piece = this.pieces[fromSquare];
        if (!piece) return;
        
        // Check if there's a piece on the destination square (capture)
        if (this.pieces[toSquare]) {
            // In a real implementation, this would handle captures
            console.log(`Captured ${this.pieces[toSquare]} on ${toSquare}`);
        }
        
        // Move the piece
        this.addPiece(toSquare, piece);
        this.removePiece(fromSquare);
        
        // Clear highlights and selection
        this.clearHighlights();
        this.selectedSquare = null;
        
        // In a real implementation, this would check for check, checkmate, etc.
        console.log(`Moved ${piece} from ${fromSquare} to ${toSquare}`);
    }
    
    highlightSquare(square) {
        const squareElement = this.boardElement.querySelector(`[data-square="${square}"]`);
        if (!squareElement) return;
        
        const highlightElement = document.createElement('div');
        highlightElement.className = 'highlight';
        squareElement.appendChild(highlightElement);
        
        this.highlightedSquares.push(square);
    }
    
    highlightMoveSquare(square) {
        const squareElement = this.boardElement.querySelector(`[data-square="${square}"]`);
        if (!squareElement) return;
        
        // Check if there's a piece on the square
        if (this.pieces[square]) {
            // Highlight as a capture
            const highlightElement = document.createElement('div');
            highlightElement.className = 'capture-highlight';
            squareElement.appendChild(highlightElement);
        } else {
            // Highlight as a move
            const highlightElement = document.createElement('div');
            highlightElement.className = 'move-highlight';
            squareElement.appendChild(highlightElement);
        }
        
        this.highlightedSquares.push(square);
    }
    
    clearHighlights() {
        for (const square of this.highlightedSquares) {
            const squareElement = this.boardElement.querySelector(`[data-square="${square}"]`);
            if (!squareElement) continue;
            
            const highlightElements = squareElement.querySelectorAll('.highlight, .move-highlight, .capture-highlight');
            highlightElements.forEach(el => squareElement.removeChild(el));
        }
        
        this.highlightedSquares = [];
    }
}

// Initialize the chessboard when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const chessboardContainer = document.getElementById('chessboard-container');
    if (chessboardContainer) {
        const board = new Chessboard('chessboard-container', {
            showCoordinates: true,
            draggable: true
        });
    }
}); 