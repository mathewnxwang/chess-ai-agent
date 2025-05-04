from pydantic import BaseModel, Field

class LLMChessMove(BaseModel):
    move: str = Field(description=(
        "The move to make in standard algebraic notation. "
        "Example of a correct response: 'e5'. "
        "Examples of incorrect responses: '2. e5' or 'e5 is the best move to play in this position.' "
    ))
    reasoning: str = Field(description=(
        "A thorough analysis of the position and of the best move to make. "
        "Speak like you are talking out loud to yourself in a casual manner."
    ))