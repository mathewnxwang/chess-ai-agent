$(document).ready(function() {
    // DOM elements
    const $board = $('#board');
    const $gameStatus = $('#game-status');
    const $resetBtn = $('#reset-btn');
    const $undoBtn = $('#undo-btn');
    const $moveList = $('#move-list');
    
    // Game state
    let game = new Chess();
    let moveHistory = [];
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
        
        // Save last move for highlighting
        lastMove = { from: source, to: target };
        
        // Add move to history
        addMoveToHistory(move);
        
        // Update game status
        updateStatus();
        
        // If the move was successful, send it to the server
        sendMoveToServer(source, target);
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
    
    // Add move to the history list
    function addMoveToHistory(move) {
        moveHistory.push(move);
        
        // Create move notation
        const moveNumber = Math.floor((moveHistory.length - 1) / 2) + 1;
        const isWhiteMove = (moveHistory.length % 2 === 1);
        const moveColor = isWhiteMove ? 'White' : 'Black';
        
        // Add move to UI
        const $moveItem = $('<div class="move-item"></div>');
        
        // Format the move notation
        const moveText = `${move.san}${move.san.includes('+') ? '' : move.san.includes('#') ? '' : (game.in_check() ? '+' : '')}`;
        
        // If it's a white move, create a new row with the move number
        if (isWhiteMove) {
            $moveItem.html(`
                <span class="move-number">${moveNumber}.</span>
                <span class="move-text">${moveText}</span>
            `);
        } else {
            // If it's a black move, append to the last row
            $moveItem.html(`
                <span class="move-number">${moveNumber}...</span>
                <span class="move-text">${moveText}</span>
            `);
        }
        
        $moveList.append($moveItem);
        
        // Scroll to the bottom of the move list
        $moveList.scrollTop($moveList[0].scrollHeight);
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
            
            // Add victory animation
            animateVictory(winner.toLowerCase());
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
    
    // Add a victory animation
    function animateVictory(winner) {
        const $board = $('.board-container');
        
        // Add a winner class to trigger animation
        $board.addClass('winner-' + winner);
        
        // Remove the class after animation
        setTimeout(() => {
            $board.removeClass('winner-' + winner);
        }, 3000);
    }
    
    // Send move to server to update backend state
    async function sendMoveToServer(from, to) {
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
            
            if (!response.ok) {
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
            $gameStatus.text('Error communicating with server');
        }
    }
    
    // Undo the last move
    function undoLastMove() {
        if (moveHistory.length === 0) return;
        
        // Undo the move in the game
        game.undo();
        
        // Remove the move from the history array
        moveHistory.pop();
        
        // Update the board position
        board.position(game.fen());
        
        // Update the move history display
        $moveList.children().last().remove();
        
        // Update the last move highlight
        if (moveHistory.length > 0) {
            const lastMoveObj = moveHistory[moveHistory.length - 1];
            lastMove = { from: lastMoveObj.from, to: lastMoveObj.to };
            highlightLastMove();
        } else {
            lastMove = null;
            $('.highlight-last-move').removeClass('highlight-last-move');
        }
        
        // Update the game status
        updateStatus();
    }
    
    // Reset the game
    async function resetGame() {
        try {
            // Reset client-side game state
            game = new Chess();
            moveHistory = [];
            lastMove = null;
            
            // Reset the UI
            board.position('start');
            $moveList.empty();
            updateStatus();
            
            // Remove any highlights
            $('.highlight-last-move').removeClass('highlight-last-move');
            
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
            $gameStatus.text('Error resetting game on server');
        }
    }
    
    // Make the board responsive
    $(window).resize(function() {
        board.resize();
    });
    
    // Add event listeners for buttons
    $resetBtn.on('click', resetGame);
    $undoBtn.on('click', undoLastMove);
    
    // Initialize game status
    updateStatus();
});