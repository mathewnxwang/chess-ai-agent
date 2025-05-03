import chess
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
import logging

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

# Global game state
board = chess.Board()

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
        "result": board.result() if board.is_game_over() else None
    }

@app.post("/move")
async def make_move(move_request: MoveRequest):
    try:
        # Log the received request for debugging
        logger.debug(f"Received move request: {move_request}")
        
        # Get the move from the request
        from_square = move_request.from_square
        to_square = move_request.to_square
        
        logger.debug(f"Attempting move from {from_square} to {to_square}")
        
        # Create the move
        move = chess.Move.from_uci(f"{from_square}{to_square}")
        
        # Check if the move is legal
        if move not in board.legal_moves:
            logger.warning(f"Illegal move attempted: {from_square}{to_square}")
            return JSONResponse(
                status_code=400,
                content={"error": "Illegal move", "fen": board.fen()}
            )
        
        # Make the move
        board.push(move)
        logger.debug(f"Move completed: {from_square}{to_square}")
        
        # Return the updated board state
        return {
            "fen": board.fen(),
            "legal_moves": [move.uci() for move in board.legal_moves],
            "is_check": board.is_check(),
            "is_checkmate": board.is_checkmate(),
            "is_game_over": board.is_game_over(),
            "result": board.result() if board.is_game_over() else None
        }
    except Exception as e:
        logger.exception(f"Error in make_move: {str(e)}")
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

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)