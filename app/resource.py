from pydantic import BaseModel, Field

class MoveRequest(BaseModel):
    from_square: str = Field(alias="from")
    to_square: str = Field(alias="to")
    
    class Config:
        validate_by_name = True

class GameState(BaseModel):
    fen: str
    legal_moves: list[str]
    is_check: bool
    is_checkmate: bool
    is_game_over: bool
    result: str | None = None
    ai_reasoning: str | None = None
