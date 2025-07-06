from pydantic import BaseModel, Field
from enum import Enum

MOVE_DESCRIPTION = """The move to make in standard algebraic notation.
Example of a correct response: 'e5'.
Examples of incorrect responses: '2. e5' or 'e5 is the best move to play in this position.'
For the love of god please don't add prefixes like '2.' or '2... ' to your move.
Black to play."""

class DecisionOptions(Enum):
    CONSIDER_NEW_MOVE = "consider_new_move"
    DECIDE_ON_MOVE = "decide_on_move"

class Decision(BaseModel):
    decision: DecisionOptions
    reasoning: str

class CounterMove(BaseModel):
    counter_move: str = Field(description="The counter move by white to consider in standard algebraic notation.")
    reasoning: str = Field(description="A thorough analysis of the counter move considered. "
        "Be concise - don't use more than three sentences. "
        "Focus on the threats that this counter move creates for black. "
        "Conclude with the strength of this counter move and how it affects the merit of the original move.")

class BaseLLMChessMove(BaseModel):
    move: str = Field(description=MOVE_DESCRIPTION)
    reasoning: str = Field(description=(
        "A thorough analysis of the position and of the move considered. "
        "Be concise - don't use more than three sentences. "
        "Try to build on the previous reasoning you explained to create a coherent thought process. "
        "After the opening, focus on tactical considerations rather than vague, positional statements. "
    ))

class AnalysisLLMChessMove(BaseLLMChessMove):
    move: str = Field(description=MOVE_DESCRIPTION)
    reasoning: str = Field(description=(
        "A thorough analysis of the position and of the move considered. "
        "Be concise - don't use more than three sentences. "
        "Try to build on the previous reasoning you explained to create a coherent thought process. "
        "After the opening, focus on tactical considerations rather than vague, positional statements. "
        "Conclude with the strength of this move based on the analysis of the counter moves considered."
    ))
    counter_moves: list[CounterMove] = Field(description="A list of counter moves by white to consider. Consider at least two moves.")
