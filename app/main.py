import chess
import chess.engine
import os
import logging
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

# Configure logging to see detailed errors
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Define request model for move
class MoveRequest(BaseModel):
    from_square: str = Field(alias="from")
    to_square: str = Field(alias="to")
    
    class Config:
        validate_by_name = True

# Game state
board = chess.Board()
engine: Optional[chess.engine.SimpleEngine] = None
stockfish_path = "/Users/mathew.wang/Downloads/stockfish/stockfish-macos-m1-apple-silicon"
ai_thinking = False
AI_SKILL_LEVEL = 5   # Default skill level (1-20)
AI_DEPTH = 10        # Default search depth
AI_ENABLED = True    # Whether AI is enabled

def initialize_engine():
    """Initialize the chess engine."""
    global engine
    
    if engine is not None:
        return
    
    try:
        # Start the engine with the specified path
        engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
        
        # Set engine options for Stockfish
        try:
            engine.configure({"Skill Level": AI_SKILL_LEVEL})
            logger.info("Stockfish initialized with skill level %s", AI_SKILL_LEVEL)
        except chess.engine.EngineError:
            logger.warning("Engine doesn't support skill level configuration")
        
    except Exception as e:
        logger.error("Error initializing Stockfish: %s", str(e))
        engine = None

def shutdown_engine():
    """Shut down the chess engine."""
    global engine
    
    if engine is not None:
        engine.quit()
        engine = None
        logger.info("Stockfish engine shut down")

def get_engine_move(board_state: chess.Board):
    """Get a move from the chess engine."""
    global engine, ai_thinking
    
    if engine is None:
        initialize_engine()
        if engine is None:
            logger.error("No chess engine available")
            return None
    
    try:
        ai_thinking = True
        logger.info("Stockfish thinking...")
        
        # Get the engine's move
        result = engine.play(board_state, chess.engine.Limit(depth=AI_DEPTH))
        move = result.move
        
        logger.info("Stockfish move: %s", move)
        ai_thinking = False
        return move
    
    except Exception as e:
        logger.error("Error getting Stockfish move: %s", str(e))
        ai_thinking = False
        return None

# Initialize engine when the app starts
@app.on_event("startup")
async def startup_event():
    initialize_engine()

# Shutdown engine when the app stops
@app.on_event("shutdown")
async def shutdown_event():
    shutdown_engine()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/board")
async def get_board():
    # Return the current board state as a FEN string
    # Also include legal moves for the UI
    return {
        "fen": board.fen(),
        "legal_moves": [move.uci() for move in board.legal_moves],
        "is_check": board.is_check(),
        "is_checkmate": board.is_checkmate(),
        "is_game_over": board.is_game_over(),
        "result": board.result() if board.is_game_over() else None,
        "ai_thinking": ai_thinking
    }

@app.post("/move")
async def make_move(move_request: MoveRequest):
    global board, ai_thinking

    try:
        # Log the received request for debugging
        logger.debug("Received move request: %s", move_request)
        
        # Get the move from the request
        from_square = move_request.from_square
        to_square = move_request.to_square
        
        logger.debug("Attempting move from %s to %s", from_square, to_square)
        
        # Create the move
        move = chess.Move.from_uci(f"{from_square}{to_square}")
        
        # Check if the move is legal
        if move not in board.legal_moves:
            logger.warning("Illegal move attempted: %s%s", from_square, to_square)
            return JSONResponse(
                status_code=400,
                content={"error": "Illegal move", "fen": board.fen()}
            )
        
        # Make the move
        board.push(move)
        logger.debug("Move completed: %s%s", from_square, to_square)
        
        # Check if it's black's turn now and the game is not over
        if board.turn == chess.BLACK and not board.is_game_over() and AI_ENABLED:
            # Set ai_thinking flag to true to indicate AI is thinking
            ai_thinking = True
            logger.debug("AI's turn")
            
            if not board.is_game_over():
                move = get_engine_move(board)
                
                if move:
                    # Make the move on the board
                    board.push(move)
                    logger.info("Stockfish made move: %s", move.uci())
            
            # Reset ai_thinking flag
            ai_thinking = False
            
            # Return the updated board state after AI move
            return {
                "fen": board.fen(),
                "legal_moves": [move.uci() for move in board.legal_moves],
                "is_check": board.is_check(),
                "is_checkmate": board.is_checkmate(),
                "is_game_over": board.is_game_over(),
                "result": board.result() if board.is_game_over() else None,
                "ai_thinking": False
            }
        
        # Otherwise, just return the current board state
        return {
            "fen": board.fen(),
            "legal_moves": [move.uci() for move in board.legal_moves],
            "is_check": board.is_check(),
            "is_checkmate": board.is_checkmate(),
            "is_game_over": board.is_game_over(),
            "result": board.result() if board.is_game_over() else None,
            "ai_thinking": False
        }
    except Exception as e:
        logger.exception("Error in make_move: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e)) from e

@app.post("/undo")
async def undo_last_move():
    global board
    
    try:
        # Undo the last two moves (player's move and AI's move)
        if len(board.move_stack) >= 2 and AI_ENABLED:
            board.pop()  # Remove AI's move
            board.pop()  # Remove player's move
        # If AI is disabled or there's only one move, just undo the last move
        elif len(board.move_stack) >= 1:
            board.pop()
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "No moves to undo"}
            )
        
        return {
            "fen": board.fen(),
            "legal_moves": [move.uci() for move in board.legal_moves],
            "is_check": board.is_check(),
            "is_checkmate": board.is_checkmate(),
            "is_game_over": board.is_game_over(),
            "result": board.result() if board.is_game_over() else None
        }
    except Exception as e:
        logger.exception(f"Error in undo_last_move: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/reset")
async def reset_board():
    global board
    
    board = chess.Board()
    return {
        "fen": board.fen(),
        "legal_moves": [move.uci() for move in board.legal_moves],
        "is_check": False,
        "is_checkmate": False,
        "is_game_over": False,
        "result": None
    }

@app.post("/set_ai_options")
async def set_ai_options(options: dict):
    global AI_SKILL_LEVEL, AI_DEPTH, AI_ENABLED, engine
    
    try:
        # Update skill level if provided
        if "skill_level" in options:
            skill = int(options["skill_level"])
            AI_SKILL_LEVEL = max(1, min(20, skill))  # Clamp between 1-20
            
            # Update engine if it's running
            if engine is not None:
                try:
                    engine.configure({"Skill Level": AI_SKILL_LEVEL})
                except chess.engine.EngineError:
                    pass  # Engine might not support this option
        
        # Update depth if provided
        if "depth" in options:
            depth = int(options["depth"])
            AI_DEPTH = max(1, min(20, depth))  # Clamp between 1-20
        
        # Update AI enabled state if provided
        if "enabled" in options:
            AI_ENABLED = bool(options["enabled"])
        
        return {
            "skill_level": AI_SKILL_LEVEL,
            "depth": AI_DEPTH,
            "enabled": AI_ENABLED
        }
    
    except Exception as e:
        logger.exception("Error setting AI options: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e)) from e

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)