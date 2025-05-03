$(document).ready(function() {
    // DOM elements
    const $board = $('#board');
    const $gameStatus = $('#game-status');
    const $resetBtn = $('#reset-btn');
    
    // Initialize the chess.js instance
    let game = new Chess();
    
    // Board configuration
    const config = {
        draggable: true,
        position: 'start',
        // Use piece theme from CDN directly
        pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{piece}.png',
        // Allow only legal moves
        onDragStart: onDragStart,
        onDrop: onDrop,
        onSnapEnd: onSnapEnd
    };
    
    // Initialize the board
    let board = Chessboard('board', config);
    
    // Only allow dragging player's own pieces
    function onDragStart(source, piece, position, orientation) {
        // Don't allow dragging if the game is over
        if (game.game_over()) return false;
        
        // Only allow white to move when it's white's turn
        if (game.turn() === 'w' && piece.search(/^b/) !== -1) {
            return false;
        }
        
        // Only allow black to move when it's black's turn
        if (game.turn() === 'b' && piece.search(/^w/) !== -1) {
            return false;
        }
        
        // Only allow white pieces to be moved initially (user always starts as white)
        if (!game.history().length && piece.search(/^b/) !== -1) {
            return false;
        }
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
        
        // Update game status
        updateStatus();
        
        // If the move was successful, send it to the server
        sendMoveToServer(source, target);
    }
    
    // Update the board position after the piece snap animation
    function onSnapEnd() {
        board.position(game.fen());
    }
    
    // Update the game status element
    function updateStatus() {
        let status = '';
        
        // Check if it's checkmate
        if (game.in_checkmate()) {
            const winner = game.turn() === 'w' ? 'Black' : 'White';
            status = `Checkmate! ${winner} wins!`;
        } 
        // Check if it's a draw
        else if (game.in_draw()) {
            status = 'Game over! Draw!';
        }
        // Game still going
        else {
            const turn = game.turn() === 'w' ? 'White' : 'Black';
            status = `${turn} to move`;
            
            // Check if in check
            if (game.in_check()) {
                status += ` (${turn} is in check!)`;
            }
        }
        
        $gameStatus.text(status);
    }
    
    // Send move to server to update backend state
    async function sendMoveToServer(from, to) {
        try {
            // Log the data being sent to the server
            console.log('Sending move to server:', { from, to });
            
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
            
            if (!response.ok) {
                // Log the response for debugging
                const errorText = await response.text();
                console.error('Server error response:', errorText);
                throw new Error(`Server returned ${response.status}: ${errorText}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                console.error(data.error);
                $gameStatus.text(data.error);
            }
        } catch (error) {
            console.error('Error sending move to server:', error);
            $gameStatus.text('Error communicating with server. The game may be out of sync.');
        }
    }
    
    // Reset the game
    async function resetGame() {
        try {
            // Reset client-side game state
            game = new Chess();
            board.position('start');
            updateStatus();
            
            // Reset server-side game state
            const response = await fetch('/reset', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.error) {
                console.error(data.error);
                $gameStatus.text(data.error);
            }
        } catch (error) {
            console.error('Error resetting game on server:', error);
            $gameStatus.text('Error resetting game on server. Please refresh the page.');
        }
    }
    
    // Add resize event to make the board responsive
    $(window).resize(function() {
        board.resize();
    });
    
    // Add reset button event listener
    $resetBtn.on('click', resetGame);
    
    // Initialize game status
    updateStatus();
});