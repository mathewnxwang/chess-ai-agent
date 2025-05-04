import logging
from typing import Optional

import chess
import chess.engine
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.agent import ChessAgent
from app.chess_helper import convert_board_to_pgn
from app.resource import GameState, MoveRequest

# Configure logging to see detailed errors
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Silence httpcore logs
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)  # Also silence httpx if you're using it

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Game state
board = chess.Board()
engine: Optional[chess.engine.SimpleEngine] = None
STOCKFISH_PATH = "/Users/mathew.wang/Downloads/stockfish/stockfish-macos-m1-apple-silicon"
AI_SKILL_LEVEL = 5   # Default skill level (1-20)
AI_DEPTH = 10        # Default search depth

chess_agent = ChessAgent()

def initialize_engine():
    """Initialize the chess engine."""
    global engine
    
    if engine is not None:
        return
    
    try:
        # Start the engine with the specified path
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        
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

def get_engine_move(board_state: chess.Board) -> chess.Move:
    """Get a move from the chess engine."""
    global engine
    
    if engine is None:
        initialize_engine()
        if engine is None:
            logger.error("No chess engine available")
            return None
    
    try:
        logger.info("Stockfish thinking...")
        
        # Get the engine's move
        result = engine.play(board_state, chess.engine.Limit(depth=AI_DEPTH))
        move = result.move
        
        logger.info("Stockfish move: %s", move)
        return move
    
    except Exception as e:
        logger.error("Error getting Stockfish move: %s", str(e))
        return None

# Initialize engine when the app starts
# @app.on_event("startup")
# async def startup_event():
#   initialize_engine()

# Shutdown engine when the app stops
@app.on_event("shutdown")
async def shutdown_event():
    shutdown_engine()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/board")
async def get_board() -> GameState:
    # Return the current board state as a FEN string
    # Also include legal moves for the UI
    return GameState(
        fen=board.fen(),
        legal_moves=[move.uci() for move in board.legal_moves],
        is_check=board.is_check(),
        is_checkmate=board.is_checkmate(),
        is_game_over=board.is_game_over(),
        result=board.result() if board.is_game_over() else None
    )

@app.post("/move/player")
async def make_player_move(move_request: MoveRequest) -> GameState:
    global board

    try:
        # Log the received request for debugging
        logger.debug("Received player move request: %s", move_request)
        
        # Get the move from the request
        from_square = move_request.from_square
        to_square = move_request.to_square
        
        logger.debug("Attempting player move from %s to %s", from_square, to_square)
        
        # Create the move
        move = chess.Move.from_uci(f"{from_square}{to_square}")
        
        # Check if the move is legal
        if move not in board.legal_moves:
            logger.warning("Illegal move attempted: %s%s", from_square, to_square)
            return JSONResponse(
                status_code=400,
                content={"error": "Illegal move", "fen": board.fen()}
            )
        
        # Make the player's move
        board.push(move)
        logger.debug("Player move completed: %s%s", from_square, to_square)
        
        # Return the updated board state after player's move
        return GameState(
            fen=board.fen(),
            legal_moves=[move.uci() for move in board.legal_moves],
            is_check=board.is_check(),
            is_checkmate=board.is_checkmate(),
            is_game_over=board.is_game_over(),
            result=board.result() if board.is_game_over() else None
        )
    except Exception as e:
        logger.exception("Error in make_player_move: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e)) from e

@app.post("/move/stockfish")
async def make_stockfish_move() -> GameState:
    global board

    try:
        # Check if it's not black's turn or game is over
        if board.turn != chess.BLACK or board.is_game_over():
            logger.warning("AI move requested when it's not AI's turn or game is over")
            return JSONResponse(
                status_code=400,
                content={"error": "Not AI's turn or game is over", "fen": board.fen()}
            )
        
        logger.debug("AI's turn")
        move = get_engine_move(board)
        
        if move:
            # Make the move on the board
            board.push(move)
            logger.info("Stockfish made move: %s", move.uci())
        else:
            logger.error("AI could not make a move")
            return JSONResponse(
                status_code=500,
                content={"error": "AI could not make a move", "fen": board.fen()}
            )
        
        # Return the updated board state after AI move
        return GameState(
            fen=board.fen(),
            legal_moves=[move.uci() for move in board.legal_moves],
            is_check=board.is_check(),
            is_checkmate=board.is_checkmate(),
            is_game_over=board.is_game_over(),
            result=board.result() if board.is_game_over() else None
        )
    except Exception as e:
        logger.exception("Error in make_ai_move: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e)) from e

@app.post("/move/llm-agent")
async def make_llm_agent_move() -> GameState:
    global board

    try:
        # Check if it's not black's turn or game is over
        if board.turn != chess.BLACK or board.is_game_over():
            logger.warning("AI move requested when it's not AI's turn or game is over")
            return JSONResponse(
                status_code=400,
                content={"error": "Not AI's turn or game is over", "fen": board.fen()}
            )
        
        logger.debug("AI turn begins")

        pgn_string = convert_board_to_pgn(board)

        move = chess_agent.make_valid_move(board=board, position=pgn_string)

        if move:
            # Make the move on the board
            board.push(move)
            logger.info("AI made move: %s", move.uci())
        else:
            logger.error("AI could not make a move")
            return JSONResponse(
                status_code=500,
                content={"error": "AI could not make a move", "fen": board.fen()}
            )
        
        # Return the updated board state after AI move
        return GameState(
            fen=board.fen(),
            legal_moves=[move.uci() for move in board.legal_moves],
            is_check=board.is_check(),
            is_checkmate=board.is_checkmate(),
            is_game_over=board.is_game_over(),
            result=board.result() if board.is_game_over() else None
        )
    except Exception as e:
        logger.exception("Error in make_ai_move: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e)) from e

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)