import chess
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Define request model for move
class MoveRequest(BaseModel):
    from_: str = None
    to: str = None

    class Config:
        # Allow from field to be mapped from "from" in JSON
        fields = {
            'from_': 'from'
        }

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
        # Get the move from the request
        from_square = move_request.from_
        to_square = move_request.to
        
        # Create the move
        move = chess.Move.from_uci(f"{from_square}{to_square}")
        
        # Check if the move is legal
        if move not in board.legal_moves:
            return JSONResponse(
                status_code=400,
                content={"error": "Illegal move", "fen": board.fen()}
            )
        
        # Make the move
        board.push(move)
        
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