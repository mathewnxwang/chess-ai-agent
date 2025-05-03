document.addEventListener('DOMContentLoaded', function() {
    const chessboard = document.getElementById('chessboard');
    const gameStatus = document.getElementById('game-status');
    const resetBtn = document.getElementById('reset-btn');
    
    // Chess piece Unicode symbols
    const pieceSymbols = {
        'p': '♟', // black pawn
        'n': '♞', // black knight
        'b': '♝', // black bishop
        'r': '♜', // black rook
        'q': '♛', // black queen
        'k': '♚', // black king
        'P': '♙', // white pawn
        'N': '♘', // white knight
        'B': '♗', // white bishop
        'R': '♖', // white rook
        'Q': '♕', // white queen
        'K': '♔'  // white king
    };
    
    // Game state
    let boardState = null;
    let selectedSquare = null;
    let legalMoves = [];
    
    // Create the chess board
    function createBoard() {
        chessboard.innerHTML = '';
        
        // Create 64 squares
        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                const square = document.createElement('div');
                square.classList.add('square');
                
                // Alternate colors
                if ((row + col) % 2 === 0) {
                    square.classList.add('white');
                } else {
                    square.classList.add('black');
                }
                
                // Set data attributes for position
                const file = String.fromCharCode(97 + col); // a, b, c, ..., h
                const rank = 8 - row; // 8, 7, 6, ..., 1
                square.dataset.position = file + rank;
                
                // Add click event
                square.addEventListener('click', handleSquareClick);
                
                chessboard.appendChild(square);
            }
        }
    }
    
    // Update the board based on FEN string
    function updateBoard(fen) {
        const fenParts = fen.split(' ');
        const position = fenParts[0];
        const rows = position.split('/');
        
        // Clear all pieces
        document.querySelectorAll('.piece').forEach(piece => piece.remove());
        
        // Add pieces based on FEN
        let rank = 8;
        for (const row of rows) {
            let file = 0;
            for (const char of row) {
                if (!isNaN(char)) {
                    // Skip empty squares
                    file += parseInt(char);
                } else {
                    // Add piece
                    const square = document.querySelector(`[data-position="${String.fromCharCode(97 + file)}${rank}"]`);
                    const piece = document.createElement('div');
                    piece.classList.add('piece');
                    piece.textContent = pieceSymbols[char];
                    piece.dataset.piece = char;
                    
                    // Add piece image if using CSS for pieces
                    const isWhite = char === char.toUpperCase();
                    const pieceType = char.toLowerCase();
                    piece.classList.add(isWhite ? 'white-piece' : 'black-piece');
                    piece.classList.add(`${pieceType}-piece`);
                    
                    square.appendChild(piece);
                    file++;
                }
            }
            rank--;
        }
        
        // Update game status
        const turn = fenParts[1] === 'w' ? 'White' : 'Black';
        gameStatus.textContent = `${turn} to move`;

        // Check for game over conditions
        if (boardState && boardState.is_checkmate) {
            const winner = turn === 'White' ? 'Black' : 'White';
            gameStatus.textContent = `Checkmate! ${winner} wins!`;
        } else if (boardState && boardState.is_check) {
            gameStatus.textContent = `${turn} is in check!`;
        } else if (boardState && boardState.is_game_over) {
            gameStatus.textContent = 'Game over! ' + (boardState.result || 'Draw');
        }
    }
    
    // Handle square click
    function handleSquareClick(event) {
        const square = event.currentTarget;
        const position = square.dataset.position;
        
        // If no square is selected and the clicked square has a piece
        if (!selectedSquare && square.querySelector('.piece')) {
            // Only allow selecting white pieces on first move
            const piece = square.querySelector('.piece').dataset.piece;
            const isWhitePiece = /[PNBRQK]/.test(piece);
            
            if (boardState && boardState.fen.includes(' b ') && isWhitePiece) {
                return; // Can't select white pieces on black's turn
            }
            
            if (boardState && boardState.fen.includes(' w ') && !isWhitePiece) {
                return; // Can't select black pieces on white's turn
            }
            
            // Select the square
            selectedSquare = position;
            square.classList.add('selected');
            
            // Highlight legal moves
            highlightLegalMoves(position);
        } 
        // If a square is already selected
        else if (selectedSquare) {
            // If same square is clicked, deselect it
            if (selectedSquare === position) {
                deselectSquare();
                return;
            }
            
            // Try to make a move
            makeMove(selectedSquare, position);
        }
    }
    
    // Highlight legal moves
    function highlightLegalMoves(position) {
        // Clear previous highlights
        document.querySelectorAll('.valid-move').forEach(square => {
            square.classList.remove('valid-move');
        });
        
        if (!boardState || !boardState.legal_moves) return;
        
        // Find moves that start from the selected position
        const legalMovesFromPosition = boardState.legal_moves.filter(move => 
            move.startsWith(position)
        );
        
        // Highlight destination squares
        legalMovesFromPosition.forEach(move => {
            const destination = move.substring(2, 4);
            const square = document.querySelector(`[data-position="${destination}"]`);
            if (square) {
                square.classList.add('valid-move');
            }
        });
    }
    
    // Deselect the currently selected square
    function deselectSquare() {
        if (selectedSquare) {
            document.querySelector(`[data-position="${selectedSquare}"]`).classList.remove('selected');
            selectedSquare = null;
            
            // Remove move highlights
            document.querySelectorAll('.valid-move').forEach(square => {
                square.classList.remove('valid-move');
            });
        }
    }
    
    // Make a move
    async function makeMove(from, to) {
        try {
            const response = await fetch('/move', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    from: from,
                    to: to
                })
            });
            
            const data = await response.json();
            
            if (data.error) {
                console.error(data.error);
                // Show error in game status
                gameStatus.textContent = data.error;
            } else {
                // Update board state
                boardState = data;
                updateBoard(data.fen);
            }
            
            // Deselect square after move attempt
            deselectSquare();
            
        } catch (error) {
            console.error('Error making move:', error);
            gameStatus.textContent = 'Error making move. Please try again.';
            deselectSquare();
        }
    }
    
    // Reset the board
    async function resetBoard() {
        try {
            const response = await fetch('/reset', {
                method: 'POST'
            });
            
            const data = await response.json();
            boardState = data;
            updateBoard(data.fen);
            deselectSquare();
            
        } catch (error) {
            console.error('Error resetting board:', error);
            gameStatus.textContent = 'Error resetting board. Please refresh the page.';
        }
    }
    
    // Initialize the board
    async function initBoard() {
        createBoard();
        
        try {
            const response = await fetch('/board');
            const data = await response.json();
            boardState = data;
            updateBoard(data.fen);
            
        } catch (error) {
            console.error('Error initializing board:', error);
            gameStatus.textContent = 'Error loading chess board. Please refresh the page.';
        }
    }
    
    // Add event listener for the reset button
    resetBtn.addEventListener('click', resetBoard);
    
    // Initialize the board
    initBoard();
});