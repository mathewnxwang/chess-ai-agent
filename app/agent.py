import chess
from app.llm import LLMManager

class ChessAgent():
    def __init__(self):
        self.llm_manager = LLMManager()

    def make_valid_move(self, board: chess.Board, position: str) -> chess.Move:

        retries = 3
        error_message = None
        while retries > 0:
            move_str = self.llm_manager.make_llm_move(position=position, error_message=error_message)

            try:
                move: chess.Move = board.parse_san(move_str)
                return move
            except chess.InvalidMoveError:
                error_message = f"Invalid move notation: '{move_str}'."
                print(error_message)
                retries -= 1
                continue
            except chess.IllegalMoveError:
                error_message = f"Illegal move: '{move_str}'."
                print(error_message)
                retries -= 1
                continue
            except chess.AmbiguousMoveError:
                error_message = f"Ambiguous move: '{move_str}'."
                print(error_message)
                retries -= 1
                continue

        raise Exception("Failed to get a valid LLM move after 3 attempts.")