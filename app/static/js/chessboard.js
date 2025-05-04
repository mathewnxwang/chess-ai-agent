$(document).ready(function() {
    // DOM elements
    const $board = $('#board');
    const $gameStatus = $('#game-status');
    
    // Game state
    let game = new Chess();
    let lastMove = null;
    
    // Board configuration
    const config = {
        draggable: true,
        position: 'start',
        // Use piece theme from CDN directly
        pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{piece}.png',
        // Allow only legal moves
        onDragStart: onDragStart,
        onDrop: onDrop,
        onSnapEnd: onSnapEnd,
        onMoveEnd: onMoveEnd
    };
    
    // Initialize the board
    let board = Chessboard('board', config);
    
    function onDragStart(source, piece, position, orientation) {
        // Don't allow dragging if the game is over
        if (game.game_over()) return false;
        
        // Only allow white to move when it's white's turn
        if (game.turn() === 'w' && piece.search(/^b/) !== -1) {
            return false;
        }

        // Only allow white pieces to be dragged
        if (piece.search(/^b/) !== -1) {
            return false;
        }

        // // Only allow black to move when it's black's turn
        // if (game.turn() === 'b' && piece.search(/^w/) !== -1) {
        //     return false;
        // }
    }
    
    // Handle piece drops
    function onDrop(source, target) {
        // Check if the move is legal
        const move = game.move({
            from: source,
            to: target,
            promotion: 'q' // Always promote to queen for simplicity
        });
        
        // If the move is illegal, return the piece to its source
        if (move === null) return 'snapback';
        
        // Save last move for highlighting
        lastMove = { from: source, to: target };
        
        // Update game status
        updateStatus();
        
        orchestrateMoves(source, target);
    }
    
    // Update the board position after the piece snap animation
    function onSnapEnd() {
        board.position(game.fen());
        
        // Highlight the last move
        highlightLastMove();
    }
    
    // After a move is completed, add subtle animation
    function onMoveEnd(oldPos, newPos) {
        $('.square-' + lastMove.to).addClass('highlight-last-move');
        $('.square-' + lastMove.from).addClass('highlight-last-move');
    }
    
    // Highlight the last move made
    function highlightLastMove() {
        // Remove previous highlights
        $('.highlight-last-move').removeClass('highlight-last-move');
        
        // Add highlight to the new move
        if (lastMove) {
            $('.square-' + lastMove.from).addClass('highlight-last-move');
            $('.square-' + lastMove.to).addClass('highlight-last-move');
        }
    }
    
    // Update the game status element with enhanced styling
    function updateStatus() {
        let status = '';
        let statusClass = 'status-badge';
        
        // Check if it's checkmate
        if (game.in_checkmate()) {
            const winner = game.turn() === 'w' ? 'Black' : 'White';
            status = `Checkmate! ${winner} wins`;
            statusClass += ' checkmate';
        } 
        // Check if it's a draw
        else if (game.in_draw()) {
            status = 'Game Over! Draw';
            statusClass += ' draw';
        }
        // Game still going
        else {
            const turn = game.turn() === 'w' ? 'White' : 'Black';
            status = `${turn} to move`;
            
            // Check if in check
            if (game.in_check()) {
                status = `${turn} is in check!`;
                statusClass += ' check';
            }
        }
        
        // Update status text and class
        $gameStatus.text(status);
        $gameStatus.attr('class', statusClass);
    }
    
    // Send player move to server
    async function sendPlayerMove(from, to) {
        try {
            const response = await fetch('/move/player', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    from: from,
                    to: to
                })
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Player move error:', errorText);
                throw new Error(`Server returned ${response.status}: ${errorText}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                console.error(data.error);
                $gameStatus.text(data.error);
                return false;
            } else {
                // Update game with server response after player's move
                game.load(data.fen);
                
                // Update the board to show the current position
                board.position(game.fen());
                
                // Highlight the last move
                highlightLastMove();
                
                // Update game status after player's move
                updateStatus();
                
                // Return whether the game is over
                return data.is_game_over;
            }
        } catch (error) {
            console.error('Error sending player move to server:', error);
            $gameStatus.text('Error communicating with server');
            return true; // Return true to prevent AI move attempt
        }
    }
    
    // Request AI move from server
    async function requestAiMove() {
        try {
            const response = await fetch('/move/ai', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('AI move error:', errorText);
                throw new Error(`Server returned ${response.status}: ${errorText}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                console.error(data.error);
                $gameStatus.text(data.error);
            } else {
                // Update game with server response after AI's move
                game.load(data.fen);
                
                // Update the last move to the AI's move
                const history = game.history({ verbose: true });
                if (history.length > 0) {
                    const lastMoveObj = history[history.length - 1];
                    lastMove = { from: lastMoveObj.from, to: lastMoveObj.to };
                }
                
                // Update the board to show the current position
                board.position(game.fen());
                
                // Highlight the last move
                highlightLastMove();
                
                // Update game status after AI move
                updateStatus();
            }
        } catch (error) {
            console.error('Error requesting AI move from server:', error);
            $gameStatus.text('Error getting AI response');
        }
    }
    
    // Handle the complete move process (player move followed by AI move)
    async function orchestrateMoves(from, to) {
        // First send the player's move
        const gameOver = await sendPlayerMove(from, to);
        
        // If the game is not over, request the AI move
        if (!gameOver && game.turn() === 'b') {
            await requestAiMove();
        }
    }
    
    // Make the board responsive
    $(window).resize(function() {
        board.resize();
    });
    
    // Initialize game status
    updateStatus();
    
    // Make sure the UI is in sync with the server on page load
    fetch('/board')
        .then(response => response.json())
        .then(data => {
            game.load(data.fen());
            board.position(data.fen());
            updateStatus();
        })
        .catch(error => {
            console.error('Error getting initial board state:', error);
        });
});