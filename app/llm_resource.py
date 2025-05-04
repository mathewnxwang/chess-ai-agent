from pydantic import BaseModel, Field
from enum import Enum

ORCHESTRATION_SYSTEM_PROMPT = """You are a grandmaster chess player playing a chess game.
You are playing for you and your family's lives so it's important to play the best moves possible with the most robust reasoning."""

ORCHESTRATION_USER_PROMPT = """You are deciding which move to play.
<current_position>
{position}
</current_position>

<previous_moves_and_reasoning>
{memory}
</previous_moves_and_reasoning>

These are your existing thoughts on the position and which move to play:
<running_thoughts>
{running_thoughts}
</running_thoughts>

Decide whether you want to want to consider a new move or if you're ready to decide on a move.

Consider a new move if you haven't already considered at least two moves."""

class DecisionOptions(Enum):
    CONSIDER_NEW_MOVE = "consider_new_move"
    DECIDE_ON_MOVE = "decide_on_move"

class Decision(BaseModel):
    decision: DecisionOptions
    reasoning: str

CONSIDER_NEW_MOVE_USER_PROMPT = """Given the position in PGN format, return the best, valid next move in standard algebraic notation that you haven't already considered.
Example of a correct response: 'e5'
Examples of incorrect responses:
- '2. e5'
- 'e5 is the best move to play in this position.'

Position: {position}

Here is each move you made previously and its reasoning:
{memory}

Here are other moves you already considered. DO NOT CHOOSE FROM THESE MOVES:
{considered_moves}

Black to play.

For the love of god please don't add prefixes like '2.' or '2... ' to your move.
"""

DECIDE_ON_MOVE_USER_PROMPT = """Given the position in PGN format, choose the best, valid next move in standard algebraic notation.

Example of a correct response: 'e5'
Examples of incorrect responses:
- '2. e5'
- 'e5 is the best move to play in this position.'

Position: {position}

Here is each move you made previously and its reasoning:
{memory}

Here are all of the moves to consider. ONLY CHOOSE FROM THESE MOVES.

Black to play.

For the love of god please don't add prefixes like '2.' or '2... ' to your move."""

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

###

SYSTEM_PROMPT = """You are a grandmaster chess player.
Given the position in PGN format, return the best, valid next move in standard algebraic notation.
Example of a correct response: 'e5'
Examples of incorrect responses:
- '2. e5'
- 'e5 is the best move to play in this position.'"""

USER_PROMPT = """Position: {position}

Here is each move you made previously and its reasoning:
{memory}

Black to play.

For the love of god please don't add prefixes like '2.' or '2... ' to your move.

Move: """

USER_PROMPT_WITH_ERROR = """
Position: {position}

Here is each move you made previously and its reasoning:
{memory}

Black to play.

Make sure to avoid this error: {error_message}

For the love of god please don't add prefixes like '2.' or '2... ' to your move.

Move: """
