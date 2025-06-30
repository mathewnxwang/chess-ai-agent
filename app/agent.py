import os
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
from langfuse import observe, get_client

langfuse = get_client()

class ChessAgent():
    def __init__(self, model: str = "gpt-4o"):
        self.llm_manager = LLMManager()
        self.memory = ""
        self.move_memory = ""
        self.considered_moves = ""
        self.model = model
        self.max_moves_to_consider = 3


    @observe()
    def make_valid_move(self, board: chess.Board, position: str) -> tuple[chess.Move, str]:
        iterations = 0
        
        while True:
            decision = self.orchestrate_action(position=position, iterations=iterations)
            iterations += 1
            if decision is not None:
                move: chess.Move = board.parse_san(decision.move)

                langfuse.update_current_span(
                    metadata={
                        "full_memory": self.memory,
                        "move_memory": self.move_memory,
                        "considered_moves": self.considered_moves,
                    }
                )
                return move, decision.reasoning
            
            # safety check to prevent infinite loop
            if iterations > 5:
                raise Exception(f"Unable to make a move.")

        raise Exception(f"Unable to make a move.")

    @observe()
    def orchestrate_action(self, position: str, iterations: int) -> LLMChessMove | None:

        decision = self.decide_on_action(position=position)

        if decision.decision == DecisionOptions.DECIDE_ON_MOVE:
            langfuse.update_current_span(
                metadata={
                    "decision": f"Agent decided to choose a move based on their analysis.",
                    "full_memory": self.memory,
                    "move_memory": self.move_memory,
                    "considered_moves": self.considered_moves,
                }
            )
            response = self.decide_on_move(position=position)
            return response
    
        if iterations > self.max_moves_to_consider:
            langfuse.update_current_span(
                metadata={
                    "decision": f"Agent decided to choose a move because they have already considered {self.max_moves_to_consider} moves.",
                    "full_memory": self.memory,
                    "move_memory": self.move_memory,
                    "considered_moves": self.considered_moves,
                }
            )
            response = self.decide_on_move(position=position)
            return response
        
        if decision.decision == DecisionOptions.CONSIDER_NEW_MOVE:
            langfuse.update_current_span(
                metadata={
                    "decision": f"Agent decided to consider a new move.",
                    "full_memory": self.memory,
                    "move_memory": self.move_memory,
                    "considered_moves": self.considered_moves,
                }
            )
            self.consider_new_move(position=position)
            return None
        
        raise Exception(f"Invalid decision from LLM: {decision.decision}")

    @observe()
    def decide_on_action(self, position: str) -> Decision:
        formatted_user_prompt = ORCHESTRATION_USER_PROMPT.format(
            position=position,
            considered_moves=self.considered_moves
        )

        llm_response = self.llm_manager.call_llm(
            model=self.model,
            system_prompt=ORCHESTRATION_SYSTEM_PROMPT,
            user_prompt=formatted_user_prompt,
            response_format=Decision,
        )

        langfuse.update_current_span(metadata={"user_prompt": formatted_user_prompt, "system_prompt": ORCHESTRATION_SYSTEM_PROMPT})

        return llm_response

    @observe()
    def consider_new_move(self, position: str) -> LLMChessMove:
        formatted_user_prompt = CONSIDER_NEW_MOVE_USER_PROMPT.format(
            position=position,
            considered_moves=self.considered_moves
        )
      
        response = self.llm_manager.call_llm(
            model=self.model,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=formatted_user_prompt,
            response_format=LLMChessMove,
        )

        self.update_move_context(response=response)

        langfuse.update_current_span(metadata={"user_prompt": formatted_user_prompt, "system_prompt": SYSTEM_PROMPT})

        return response

    @observe()
    def decide_on_move(self, position: str) -> LLMChessMove:
        formatted_user_prompt = DECIDE_ON_MOVE_USER_PROMPT.format(position=position, considered_moves=self.considered_moves)

        response = self.llm_manager.call_llm(
            model=self.model,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=formatted_user_prompt,
            response_format=LLMChessMove,
        )

        langfuse.update_current_span(metadata={"user_prompt": formatted_user_prompt, "system_prompt": SYSTEM_PROMPT})

        return response

    @observe()
    def update_move_context(self, response: LLMChessMove) -> None:
        if self.move_memory == "":
            memory_addition = f"{response.move}: {response.reasoning}"
        else:
            memory_addition = f"\n\n{response.move}: {response.reasoning}"

        if self.considered_moves == "":
            considered_move = response.move
        else:
            considered_move = f"\n{response.move}"

        self.memory += memory_addition
        self.considered_moves += considered_move

        langfuse.update_current_span(metadata={"new_move_memory": memory_addition, "full_move_memory": self.memory, "considered_moves": self.considered_moves})

