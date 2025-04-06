document.addEventListener('DOMContentLoaded', function() {
    const chessboard = document.getElementById('chessboard');
    const status = document.getElementById('status');
    const difficultySelect = document.getElementById('difficulty');
    const resetBtn = document.getElementById('reset-btn');
    const startAsBlackBtn = document.getElementById('start-as-black');
    let game, aiLevel = 1;
    let userColor = 'w';
    let draggedPiece = null;
    let isDragging = false;
    let gameInProgress = false;
    let boardPosition = {};

    // Initialize the game
    function initGame() {
        game = new Chess();
        updateStatus();
        renderBoard();
        gameInProgress = true;
    }

    // Function to get piece image URL
    function getPieceImageUrl(piece) {
        if (!piece) return null;
        
        const color = piece.color === 'w' ? 'white' : 'black';
        const pieceType = {
            'p': 'pawn',
            'r': 'rook',
            'n': 'knight',
            'b': 'bishop',
            'q': 'queen',
            'k': 'king'
        }[piece.type];
        
        return `/static/assets/pieces/${color}_${pieceType}.png`;
    }

    // Render the chessboard with pieces
    function renderBoard() {
        chessboard.innerHTML = '';
        const position = game.board();

        for (let i = 0; i < 8; i++) {
            for (let j = 0; j < 8; j++) {
                const row = userColor === 'w' ? 7 - i : i;
                const col = userColor === 'w' ? j : 7 - j;
                
                const square = document.createElement('div');
                square.classList.add('square');
                square.classList.add((row + col) % 2 === 0 ? 'light' : 'dark');
                
                const piece = position[row][col];
                if (piece) {
                    const pieceElement = document.createElement('div');
                    pieceElement.classList.add('piece');
                    pieceElement.setAttribute('data-piece', piece.color + piece.type);
                    pieceElement.setAttribute('data-square', String.fromCharCode(97 + col) + (8 - row));
                    pieceElement.style.backgroundImage = `url('${getPieceImageUrl(piece)}')`;
                    
                    // Add drag functionality only for user's pieces
                    if (piece.color === userColor && gameInProgress) {
                        pieceElement.draggable = true;
                        pieceElement.addEventListener('dragstart', dragStart);
                        pieceElement.addEventListener('touchstart', touchStart, { passive: false });
                    }
                    
                    square.appendChild(pieceElement);
                }
                
                square.setAttribute('data-square', String.fromCharCode(97 + col) + (8 - row));
                square.addEventListener('dragover', dragOver);
                square.addEventListener('drop', drop);
                square.addEventListener('click', handleSquareClick);
                
                chessboard.appendChild(square);
            }
        }
        
        // Add row and column labels
        addBoardLabels();
    }

    // Add chess board labels (a-h, 1-8)
    function addBoardLabels() {
        // Add code for board labels if needed
    }

    // Handle dragging start
    function dragStart(e) {
        draggedPiece = {
            element: this,
            square: this.getAttribute('data-square')
        };
        setTimeout(() => {
            this.style.opacity = '0.4';
        }, 0);
    }

    // Touch events for mobile support
    function touchStart(e) {
        // Add touch event handling if needed
    }

    // Prevent default on drag over
    function dragOver(e) {
        e.preventDefault();
    }

    // Handle piece drop
    function drop(e) {
        e.preventDefault();
        
        if (draggedPiece) {
            const targetSquare = this.getAttribute('data-square');
            const move = {
                from: draggedPiece.square,
                to: targetSquare,
                promotion: 'q' // Auto-promote to queen
            };
            
            // Make the move if it's legal
            if (makeMove(move)) {
                setTimeout(makeAiMove, 300);
            }
            
            // Reset the dragged piece
            draggedPiece.element.style.opacity = '1';
            draggedPiece = null;
        }
    }

    // Handle square click (for click-based movement)
    function handleSquareClick(e) {
        // Add code for click-based movement if needed
    }

    // Make a move and update the board
    function makeMove(move) {
        const result = game.move(move);
        if (result) {
            updateStatus();
            renderBoard();
            return true;
        }
        return false;
    }

    // Make AI move
    function makeAiMove() {
        if (game.game_over() || game.turn() !== (userColor === 'w' ? 'b' : 'w')) return;
        
        // Use setTimeout to make it feel more natural
        setTimeout(() => {
            // AI move logic would go here
            // For example, using a chess engine API
            
            updateStatus();
            renderBoard();
        }, 500);
    }

    // Update game status
    function updateStatus() {
        let statusText = '';
        
        if (game.in_checkmate()) {
            statusText = 'Game over, ' + (game.turn() === 'w' ? 'black' : 'white') + ' wins by checkmate!';
            gameInProgress = false;
        } else if (game.in_draw()) {
            statusText = 'Game over, drawn position';
            gameInProgress = false;
        } else {
            statusText = (game.turn() === 'w' ? 'White' : 'Black') + ' to move';
            if (game.in_check()) {
                statusText += ', ' + (game.turn() === 'w' ? 'White' : 'Black') + ' is in check';
            }
        }
        
        status.textContent = statusText;
        
        // If game is over, record it
        if (!gameInProgress) {
            recordGameResult();
        }
    }

    // Record game result to the server
    function recordGameResult() {
        // Add game recording logic if needed
    }

    // Setup event listeners
    resetBtn.addEventListener('click', () => {
        initGame();
    });

    startAsBlackBtn.addEventListener('click', () => {
        userColor = 'b';
        initGame();
        setTimeout(makeAiMove, 500);
    });

    difficultySelect.addEventListener('change', () => {
        aiLevel = parseInt(difficultySelect.value);
    });

    // Start the game
    initGame();
});