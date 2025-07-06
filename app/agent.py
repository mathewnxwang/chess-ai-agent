import os
import chess
from dotenv import load_dotenv
from app.llm import LLMManager
from app.llm_resource import (
    AnalysisLLMChessMove,
    Decision,
    DecisionOptions,
    BaseLLMChessMove,
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
        self.game_memory: list[str] = []
        self.analysis_memory: list[str] = []
        self.model = model
        self.max_moves_to_consider = 3

    def _get_previous_moves(self) -> str:
        if not self.game_memory:
            return "No moves have been made yet."
        # only inject the last 3 game moves
        return "\n".join(self.game_memory[-3:])

    def _get_considered_moves(self) -> str:
        if not self.analysis_memory:
            return "No moves have been considered yet."
        return "\n".join(self.analysis_memory)

    def _update_analysis_memory(self, move: AnalysisLLMChessMove) -> None:
        self.analysis_memory.append(f"{move.move}: {move.reasoning}")

    def _clear_analysis_memory(self) -> None:
        self.analysis_memory = []
    
    def _update_game_memory(self, move: BaseLLMChessMove) -> None:
        self.game_memory.append(f"{move.move}: {move.reasoning}")

    @observe()
    def make_valid_move(self, board: chess.Board, position: str) -> tuple[chess.Move, str]:
        iterations = 0
        
        while True:
            decision = self.decide_on_action(position=position)
            move = self.execute_decision(position=position, decision=decision, iterations=iterations)
            iterations += 1

            if move is not None:
                return self.post_process_move(board=board, move=move)
            
            # safety check to prevent infinite loop
            if iterations > 5:
                raise Exception("Unable to make a move.")

        raise Exception("Unable to make a move.")

    @observe()
    def decide_on_action(self, position: str) -> Decision:

        previous_moves = self._get_previous_moves()
        considered_moves = self._get_considered_moves()

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
    def execute_decision(self, position: str, decision: Decision, iterations: int) -> BaseLLMChessMove | None:

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
            #TODO: returning None here is weird
            return None
        
        raise Exception(f"Invalid decision from LLM: {decision.decision}")

    @observe()
    def post_process_move(self, board: chess.Board, move: BaseLLMChessMove) -> tuple[chess.Move, str]:
        move_object: chess.Move = board.parse_san(move.move)

        langfuse.update_current_span(
            metadata={
                "game_memory": self.game_memory,
                "analysis_memory": self.analysis_memory,
            }
        )
        self._update_game_memory(move)
        self._clear_analysis_memory()

        return move_object, move.reasoning

    @observe()
    def decide_on_move(self, position: str, decision_reasoning: str | None = None) -> BaseLLMChessMove:

        previous_moves = self._get_previous_moves()
        considered_moves = self._get_considered_moves()

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
            response_format=BaseLLMChessMove,
        )

        langfuse.update_current_span(metadata={"user_prompt": formatted_user_prompt, "system_prompt": SYSTEM_PROMPT})

        return response

    @observe()
    def consider_new_move(self, position: str) -> AnalysisLLMChessMove:

        previous_moves = self._get_previous_moves()
        considered_moves = self._get_considered_moves()

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
            response_format=AnalysisLLMChessMove,
        )

        self._update_analysis_memory(response)

        langfuse.update_current_span(metadata={"user_prompt": formatted_user_prompt, "system_prompt": SYSTEM_PROMPT})

        return response


