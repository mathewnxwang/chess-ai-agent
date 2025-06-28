import logging
from typing import Optional

import chess
import chess.engine
from fastapi import FastAPI, HTTPException, Request, Depends
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


class GameManager:
    """Manages game state and chess agent."""
    
    def __init__(self):
        self.board = chess.Board()
        self.chess_agent = ChessAgent()
    
    def get_board(self) -> chess.Board:
        return self.board
    
    def get_agent(self) -> ChessAgent:
        return self.chess_agent
    
    def reset_game(self):
        """Reset the game to initial state."""
        self.board = chess.Board()


# Create a single instance of the game manager
game_manager = GameManager()


def get_game_manager() -> GameManager:
    """Dependency injection function to get the game manager."""
    return game_manager


app = FastAPI()

# Global exception handlers
@app.exception_handler(chess.InvalidMoveError)
async def chess_invalid_move_handler(request: Request, exc: chess.InvalidMoveError):
    logger.warning("Invalid chess move attempted: %s", str(exc))
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid chess move", "detail": str(exc)}
    )

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    logger.warning("Value error in chess operation: %s", str(exc))
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid input", "detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception occurred: %s", str(exc))
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "An unexpected error occurred"}
    )

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/board")
async def get_board(game_manager: GameManager = Depends(get_game_manager)) -> GameState:
    board = game_manager.get_board()
    return GameState(
        fen=board.fen(),
        legal_moves=[move.uci() for move in board.legal_moves],
        is_check=board.is_check(),
        is_checkmate=board.is_checkmate(),
        is_game_over=board.is_game_over(),
        result=board.result() if board.is_game_over() else None
    )

@app.post("/move/player")
async def make_player_move(
    move_request: MoveRequest, 
    game_manager: GameManager = Depends(get_game_manager)
) -> GameState:
    board = game_manager.get_board()

    logger.debug("Received player move request: %s", move_request)
    
    from_square = move_request.from_square
    to_square = move_request.to_square
    
    logger.debug("Attempting player move from %s to %s", from_square, to_square)
    
    move = chess.Move.from_uci(f"{from_square}{to_square}")
    
    if move not in board.legal_moves:
        logger.warning("Illegal move attempted: %s%s", from_square, to_square)
        raise HTTPException(status_code=400, detail="Illegal move")
    
    board.push(move)
    logger.debug("Player move completed: %s%s", from_square, to_square)
    
    return GameState(
        fen=board.fen(),
        legal_moves=[move.uci() for move in board.legal_moves],
        is_check=board.is_check(),
        is_checkmate=board.is_checkmate(),
        is_game_over=board.is_game_over(),
        result=board.result() if board.is_game_over() else None
    )

@app.post("/move/llm-agent")
async def make_llm_agent_move(
    game_manager: GameManager = Depends(get_game_manager)
) -> GameState:
    board = game_manager.get_board()
    chess_agent = game_manager.get_agent()

    # Check if it's not black's turn or game is over
    if board.turn != chess.BLACK or board.is_game_over():
        logger.warning("AI move requested when it's not AI's turn or game is over")
        raise HTTPException(status_code=400, detail="Not AI's turn or game is over")
    
    logger.debug("AI turn begins")

    pgn_string = convert_board_to_pgn(board)
    move_result = chess_agent.make_valid_move(board=board, position=pgn_string)
    
    if not move_result:
        logger.error("AI could not make a move")
        return HTTPException(status_code=500, detail="AI could not make a move")
        
    move, reasoning = move_result
    
    logger.info("AI made move: %s", move.uci())
    logger.info("AI reasoning: %s", reasoning)
    
    board.push(move)
    
    return GameState(
        fen=board.fen(),
        legal_moves=[move.uci() for move in board.legal_moves],
        is_check=board.is_check(),
        is_checkmate=board.is_checkmate(),
        is_game_over=board.is_game_over(),
        result=board.result() if board.is_game_over() else None,
        ai_reasoning=reasoning
    )

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)