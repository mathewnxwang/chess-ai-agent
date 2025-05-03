$(document).ready(function() {
    // DOM elements
    const $board = $('#board');
    const $gameStatus = $('#game-status');
    const $resetBtn = $('#reset-btn');
    const $undoBtn = $('#undo-btn');
    const $moveList = $('#move-list');
    const $skillLevel = $('#skill-level');
    const $searchDepth = $('#search-depth');
    const $applySettings = $('#apply-settings');
    
    // Game state
    let game = new Chess();
    let moveHistory = [];
    let lastMove = null;
    let boardUpdateInterval = null;
    
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
    
    // These functions are no longer needed as AI moves are made immediately
    // and returned in the response to the user's move
    function startPolling() {
        // No longer needed - AI moves immediately
        console.log("Polling no longer needed - AI moves immediately");
    }
    
    function stopPolling() {
        // Clean up any existing interval just in case
        if (boardUpdateInterval) {
            clearInterval(boardUpdateInterval);
            boardUpdateInterval = null;
        }
    }
    
    // This function is kept for backwards compatibility but is no longer needed
    async function checkForAiMove() {
        console.log("Manual check for AI move - should not be needed");
        try {
            const response = await fetch('/board');
            const data = await response.json();
            
            // Update the game state with the server state
            game.load(data.fen);
            updateBoardAfterServerMove(data);
        } catch (error) {
            console.error('Error checking for AI move:', error);
        }
    }
    
    // Helper function to update the board after receiving a move from the server
    function updateBoardAfterServerMove(data) {
        // Get the last move from the move stack
        if (game.history().length > moveHistory.length) {
            // Get the last move made
            const moveObj = game.history({ verbose: true }).pop();
            
            if (moveObj) {
                // Update last move for highlighting
                lastMove = { from: moveObj.from, to: moveObj.to };
                
                // Add the move to our history
                addMoveToHistory(moveObj);
                
                // Update the board
                board.position(game.fen());
                
                // Highlight the move
                highlightLastMove();
                
                // Update game status
                updateStatus();
            }
        }
    }
    
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
        
        // Only allow white pieces to be moved (user always plays as white)
        if (piece.search(/^b/) !== -1) {
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
        
        // Send the move to the server - the AI's response will be handled in sendMoveToServer
        sendMoveToServer(source, target);
        
        // No need to poll - AI moves immediately and response is in sendMoveToServer
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
    
    // Send move to server to update backend state and get AI's response
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
            } else {
                // Update game with server response (which now includes AI's move if made)
                game.load(data.fen);
                
                // Only update UI if AI made a move (if length of move history changed)
                if (game.history().length > moveHistory.length + 1) {
                    // This means both player move and AI move are in the new FEN
                    // First, get the last two moves
                    const history = game.history({ verbose: true });
                    const aiMove = history[history.length - 1];
                    
                    if (aiMove) {
                        console.log('AI responded with move:', aiMove.san);
                        
                        // Update last move for highlighting (to the AI's move)
                        lastMove = { from: aiMove.from, to: aiMove.to };
                        
                        // Add both moves to history
                        // The player's move was already added in onDrop
                        addMoveToHistory(aiMove);
                        
                        // Update the board to show the AI's move
                        board.position(data.fen);
                        
                        // Highlight the AI's move
                        highlightLastMove();
                    }
                }
                
                // Update game status after AI move
                updateStatus();
            }
        } catch (error) {
            console.error('Error sending move to server:', error);
            $gameStatus.text('Error communicating with server');
        }
    }
    
    // Apply AI settings to the server
    async function applyAiSettings() {
        try {
            const skillLevel = parseInt($skillLevel.val());
            const searchDepth = parseInt($searchDepth.val());
            
            const response = await fetch('/set_ai_options', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    skill_level: skillLevel,
                    depth: searchDepth,
                    enabled: true
                })
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Server error response:', errorText);
                throw new Error(`Server returned ${response.status}: ${errorText}`);
            }
            
            const data = await response.json();
            console.log('AI settings updated:', data);
            
            // Show success indicator
            $applySettings.html('<i class="fas fa-check"></i> Settings Applied');
            
            // Reset button text after 2 seconds
            setTimeout(() => {
                $applySettings.html('<i class="fas fa-check"></i> Apply Settings');
            }, 2000);
            
        } catch (error) {
            console.error('Error applying AI settings:', error);
            $gameStatus.text('Error updating AI settings');
        }
    }
    
    // Undo the last move
    async function undoLastMove() {
        try {
            const response = await fetch('/undo', {
                method: 'POST'
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
            } else {
                // Reset the client-side game state
                game.load(data.fen);
                
                // Reset move history (simplest approach is to clear and rebuild from the game history)
                moveHistory = [];
                $moveList.empty();
                
                // Rebuild move history from game
                const verboseMoves = game.history({ verbose: true });
                verboseMoves.forEach(move => {
                    addMoveToHistory(move);
                });
                
                // Update the board position
                board.position(game.fen());
                
                // Update last move highlight
                if (verboseMoves.length > 0) {
                    const lastMoveObj = verboseMoves[verboseMoves.length - 1];
                    lastMove = { from: lastMoveObj.from, to: lastMoveObj.to };
                    highlightLastMove();
                } else {
                    lastMove = null;
                    $('.highlight-last-move').removeClass('highlight-last-move');
                }
                
                // Update the game status
                updateStatus();
            }
        } catch (error) {
            console.error('Error undoing move:', error);
            $gameStatus.text('Error undoing move');
        }
    }
    
    // Reset the game
    async function resetGame() {
        try {
            // Reset server-side game state
            const response = await fetch('/reset', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.error) {
                console.error(data.error);
                $gameStatus.text(data.error);
            } else {
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
                
                // Stop polling if active
                stopPolling();
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
    $applySettings.on('click', applyAiSettings);
    
    // Initialize game status
    updateStatus();
    
    // Make sure the UI is in sync with the server on page load
    fetch('/board')
        .then(response => response.json())
        .then(data => {
            game.load(data.fen);
            board.position(data.fen);
            
            // Rebuild move history if needed
            if (game.history().length > 0) {
                const verboseMoves = game.history({ verbose: true });
                verboseMoves.forEach(move => {
                    addMoveToHistory(move);
                });
                
                const lastMoveObj = verboseMoves[verboseMoves.length - 1];
                lastMove = { from: lastMoveObj.from, to: lastMoveObj.to };
                highlightLastMove();
            }
            
            updateStatus();
            
            // If it's black's turn, immediately fetch the latest board state
            if (game.turn() === 'b' && !game.game_over()) {
                checkForAiMove();  // This will just update the UI with the current state
            }
        })
        .catch(error => {
            console.error('Error getting initial board state:', error);
        });
});