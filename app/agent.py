import chess
from app.llm import LLMManager
from app.llm_resource import (
    Decision,
    DecisionOptions,
    LLMChessMove,
)
from app.prompts import (
    ORCHESTRATION_SYSTEM_PROMPT,
    ORCHESTRATION_USER_PROMPT,
    USER_PROMPT_WITH_ERROR,
    USER_PROMPT,
    SYSTEM_PROMPT,
    CONSIDER_NEW_MOVE_USER_PROMPT,
    DECIDE_ON_MOVE_USER_PROMPT,
)

class ChessAgent():
    def __init__(self, model: str = "gpt-4o"):
        self.llm_manager = LLMManager()
        self.memory = ""
        self.move_memory = ""
        self.considered_moves = ""
        self.model = model
        self.max_moves_to_consider = 3

    def make_valid_move(self, board: chess.Board, position: str) -> tuple[chess.Move, str]:
        iterations = 0
        
        while True:
            decision = self.decide_on_action(position=position, iterations=iterations)
            iterations += 1
            if decision is not None:
                move: chess.Move = board.parse_san(decision.move)
                return move, decision.reasoning
            
            # safety check to prevent infinite loop
            if iterations > 5:
                raise Exception(f"Unable to make a move.")

        raise Exception(f"Unable to make a move.")

    def decide_on_action(self, position: str, iterations: int) -> LLMChessMove | None:
        formatted_user_prompt = ORCHESTRATION_USER_PROMPT.format(
            position=position,
            considered_moves=self.move_memory
        )

        llm_response = self.llm_manager.call_llm(
            model=self.model,
            system_prompt=ORCHESTRATION_SYSTEM_PROMPT,
            user_prompt=formatted_user_prompt,
            response_format=Decision,
        )

        # do not consider more than 3 moves
        if llm_response.decision == DecisionOptions.DECIDE_ON_MOVE or iterations > self.max_moves_to_consider:
            response = self.decide_on_move(position=position)
            return response
        
        if llm_response.decision == DecisionOptions.CONSIDER_NEW_MOVE:
            self.consider_new_move(position=position)
            return None
        
        raise Exception(f"Invalid decision from LLM: {llm_response.decision}")

    def consider_new_move(self, position: str) -> LLMChessMove:
        formatted_user_prompt = CONSIDER_NEW_MOVE_USER_PROMPT.format(
            position=position,
            considered_moves=self.move_memory
        )
      
        response = self.llm_manager.call_llm(
            model=self.model,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=formatted_user_prompt,
            response_format=LLMChessMove,
        )

        self.update_move_context(response=response)

        return response

    def decide_on_move(self, position: str) -> LLMChessMove:
        formatted_user_prompt = DECIDE_ON_MOVE_USER_PROMPT.format(position=position, considered_moves=self.considered_moves)

        response = self.llm_manager.call_llm(
            model=self.model,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=formatted_user_prompt,
            response_format=LLMChessMove,
        )
        return response

    def update_move_context(self, response: LLMChessMove) -> None:
        if self.move_memory == "":
            memory_addition = f"{response.move}: {response.reasoning}"
        else:
            memory_addition = f"\n{response.move}: {response.reasoning}"

        print(f"New move memory formed: {memory_addition}")
        self.memory += memory_addition
        print("Added new considered move to the existing move memory.")
