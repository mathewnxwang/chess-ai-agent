from pydantic import BaseModel, Field
from enum import Enum

class DecisionOptions(Enum):
    CONSIDER_NEW_MOVE = "consider_new_move"
    DECIDE_ON_MOVE = "decide_on_move"

class Decision(BaseModel):
    decision: DecisionOptions
    reasoning: str

class LLMChessMove(BaseModel):
    move: str = Field(description=(
        "The move to make in standard algebraic notation. "
        "Example of a correct response: 'e5'. "
        "Examples of incorrect responses: '2. e5' or 'e5 is the best move to play in this position.' "
    ))
    reasoning: str = Field(description=(
        "A thorough analysis of the position and of the move considered. "
        "Be concise - don't use more than three sentences. "
        "Try to build on the previous reasoning you explained to create a coherent thought process."
    ))

