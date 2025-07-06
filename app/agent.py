import os
import chess
from dotenv import load_dotenv
from app.llm import LLMManager
from app.llm_resource import (
    Decision,
    DecisionOptions,
    LLMChessMove,
)
from app.prompts import (
    BASE_MOVE_PROMPT,
    SYSTEM_PROMPT,
    ORCHESTRATION_USER_PROMPT,
    CONSIDER_NEW_MOVE_USER_PROMPT,
    DECIDE_ON_MOVE_USER_PROMPT,
)
from langfuse import observe, get_client

load_dotenv("secrets.env")

langfuse = get_client()


class ChessAgent():
    def __init__(self, model: str = "gpt-4o"):
        self.llm_manager = LLMManager()
        self.game_memory = []
        self.analysis_memory = ""
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
                        "game_memory": self.game_memory,
                        "analysis_memory": self.analysis_memory,
                    }
                )
                # clear the analysis memory after a move is made
                self.analysis_memory = ""
                # update the game memory with the actual move made
                self.game_memory.append(f"{move}: {decision.reasoning}")
                return move, decision.reasoning
            
            # safety check to prevent infinite loop
            if iterations > 5:
                raise Exception("Unable to make a move.")

        raise Exception("Unable to make a move.")

    @observe()
    def orchestrate_action(self, position: str, iterations: int) -> LLMChessMove | None:

        decision = self.decide_on_action(position=position)

        if decision.decision == DecisionOptions.DECIDE_ON_MOVE:
            decision_reasoning = decision.reasoning
            langfuse.update_current_span(
                metadata={
                    "decision": "Agent decided to choose a move based on their analysis.",
                    "game_memory": self.game_memory,
                    "analysis_memory": self.analysis_memory,
                }
            )
            response = self.decide_on_move(position=position, decision_reasoning=decision_reasoning)
            return response
    
        if iterations > self.max_moves_to_consider:
            langfuse.update_current_span(
                metadata={
                    "decision": f"Agent decided to choose a move because they have already considered {self.max_moves_to_consider} moves.",
                    "game_memory": self.game_memory,
                    "analysis_memory": self.analysis_memory,
                }
            )
            response = self.decide_on_move(position=position)
            return response
        
        if decision.decision == DecisionOptions.CONSIDER_NEW_MOVE:
            langfuse.update_current_span(
                metadata={
                    "decision": "Agent decided to consider a new move.",
                    "game_memory": self.game_memory,
                    "analysis_memory": self.analysis_memory,
                }
            )
            self.consider_new_move(position=position)
            return None
        
        raise Exception(f"Invalid decision from LLM: {decision.decision}")

    @observe()
    def decide_on_action(self, position: str) -> Decision:

        if self.game_memory == "":
            previous_moves = "No moves have been made yet."
        else:
            # only inject the last 3 game moves
            previous_moves = "\n".join(self.game_memory[-3:])
        
        if self.analysis_memory == "":
            considered_moves = "No moves have been considered yet."
        else:
            considered_moves = self.analysis_memory

        formatted_user_prompt = ORCHESTRATION_USER_PROMPT.format(
            position=position,
            previous_moves=previous_moves,
            considered_moves=considered_moves,
        )

        llm_response = self.llm_manager.call_llm(
            model=self.model,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=formatted_user_prompt,
            response_format=Decision,
        )

        langfuse.update_current_span(metadata={"user_prompt": formatted_user_prompt, "system_prompt": SYSTEM_PROMPT})

        return llm_response

    @observe()
    def consider_new_move(self, position: str) -> LLMChessMove:

        if self.game_memory == "":
            previous_moves = "No moves have been made yet."
        else:
            # only inject the last 3 game moves
            previous_moves = "\n".join(self.game_memory[-3:])
        
        if self.analysis_memory == "":
            considered_moves = "No moves have been considered yet."
        else:
            considered_moves = self.analysis_memory

        base_move_prompt = BASE_MOVE_PROMPT.format(
            position=position,
            previous_moves=previous_moves,
        )
        formatted_user_prompt = CONSIDER_NEW_MOVE_USER_PROMPT.format(
            base_move_prompt=base_move_prompt,
            considered_moves=considered_moves,
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
    def decide_on_move(self, position: str, decision_reasoning: str | None = None) -> LLMChessMove:

        if self.game_memory == "":
            previous_moves = "No moves have been made yet."
        else:
            # only inject the last 3 game moves
            previous_moves = "\n".join(self.game_memory[-3:])
        
        if self.analysis_memory == "":
            considered_moves = "No moves have been considered yet."
        else:
            considered_moves = self.analysis_memory

        base_move_prompt = BASE_MOVE_PROMPT.format(
            position=position,
            previous_moves=previous_moves,
        )
        formatted_user_prompt = DECIDE_ON_MOVE_USER_PROMPT.format(
            base_move_prompt=base_move_prompt,
            considered_moves=considered_moves,
            decision_reasoning=decision_reasoning,
        )

        response = self.llm_manager.call_llm(
            model=self.model,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=formatted_user_prompt,
            response_format=LLMChessMove,
        )

        langfuse.update_current_span(metadata={"user_prompt": formatted_user_prompt, "system_prompt": SYSTEM_PROMPT})

        return response

    def update_move_context(self, response: LLMChessMove) -> None:
        if self.analysis_memory == "":
            memory_addition = f"{response.move}: {response.reasoning}"
        else:
            memory_addition = f"\n\n{response.move}: {response.reasoning}"

        self.analysis_memory += memory_addition
        langfuse.update_current_span(metadata={"analysis_memory_added": memory_addition, "new_analysis_memory": self.analysis_memory})

