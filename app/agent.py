import chess
from app.llm import LLMManager
from app.llm_resource import (
    Decision,
    DecisionOptions,
    ORCHESTRATION_SYSTEM_PROMPT,
    ORCHESTRATION_USER_PROMPT,
    USER_PROMPT_WITH_ERROR,
    USER_PROMPT,
    SYSTEM_PROMPT,
    LLMChessMove,
    CONSIDER_NEW_MOVE_USER_PROMPT,
    DECIDE_ON_MOVE_USER_PROMPT,
)

class ChessAgent():
    def __init__(self, model: str = "gpt-4o"):
        self.llm_manager = LLMManager()
        self.memory = ""
        self.considered_moves = ""
        self.iterations = 0
        self.model = model

    def make_valid_move(self, board: chess.Board, position: str) -> tuple[chess.Move, str]:
        thinking = True
        while thinking:
            decision = self.decide_on_action(board=board, position=position)
            self.iterations += 1
            if self.iterations > 6:
                raise Exception("Failed to make a valid move after 5 iterations.")
            if decision:
                thinking = False

        move: chess.Move = board.parse_san(decision.move)
        return move, decision.reasoning

    def decide_on_action(self, board: chess.Board, position: str) -> LLMChessMove | None:
        llm_response = self.llm_manager.call_llm(
            model=self.model,
            system_prompt=ORCHESTRATION_SYSTEM_PROMPT,
            user_prompt=ORCHESTRATION_USER_PROMPT,
            response_format=Decision,
        )

        if llm_response.decision == DecisionOptions.DECIDE_ON_MOVE or self.iterations > 3:
            response = self.decide_on_move(position=position)
            return response
        
        if llm_response.decision == DecisionOptions.CONSIDER_NEW_MOVE:
            self.get_llm_move(board=board, position=position)
            return None
        
        raise Exception(f"Invalid decision from LLM: {llm_response.decision}")


    def get_llm_move(self, board: chess.Board, position: str) -> None:
        """
        Adds a move and its reasoning to memory.
        """
        retries = 3
        error_message = None
        while retries > 0:
            try:
                llm_response = self.make_llm_move(position=position, error_message=error_message)
                move_str = llm_response.move
                reasoning = llm_response.reasoning
                return None

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

    def make_llm_move(self, position: str, error_message: str | None) -> LLMChessMove:
        """
        Get a move from the LLM. Returns the full LLMChessMove object with move and reasoning.
        """
        if error_message:
            # handle this with retries eventually
            raise Exception(f"Error message: {error_message}")
            # formatted_user_prompt = USER_PROMPT_WITH_ERROR.format(position=position, memory=self.memory, error_message=error_message)
        else:
            formatted_user_prompt = CONSIDER_NEW_MOVE_USER_PROMPT.format(position=position, memory=self.memory, considered_moves=self.considered_moves)
        
        response = self.llm_manager.call_llm(
            model=self.model,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=formatted_user_prompt,
            response_format=LLMChessMove,
        )

        if self.memory == "":
            memory_addition = f"{response.move}: {response.reasoning}"
        else:
            memory_addition = f"\n{response.move}: {response.reasoning}"

        print(f"New memory formed: {memory_addition}")
        self.memory += memory_addition
        print("Added new memory to existing memory.")

        if self.considered_moves == "":
            self.considered_moves = response.move
        else:
            self.considered_moves += f", {response.move}"
        print(f"Updated considered moves, which now looks like: {self.considered_moves}")

        return response
    
    def decide_on_move(self, position: str) -> LLMChessMove:
        formatted_user_prompt = DECIDE_ON_MOVE_USER_PROMPT.format(position=position, memory=self.memory, considered_moves=self.considered_moves)

        response = self.llm_manager.call_llm(
            model=self.model,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=formatted_user_prompt,
            response_format=LLMChessMove,
        )
        return response
