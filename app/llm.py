import os
from dotenv import load_dotenv
import logging
from pydantic import BaseModel
from typing import TypeVar

from openai import OpenAI
from openai.types.responses.parsed_response import (
    ParsedResponse,
    ParsedResponseOutputMessage,
)

from app.llm_resource import LLMChessMove

# Configure logging for OpenAI
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

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

class LLMManager():
    def __init__(self):
        load_dotenv("secrets.env")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=openai_api_key)
        self.memory = ""

    def call_llm(
            self,
            model: str,
            system_prompt: str,
            user_prompt: str,
            temperature: float = 1,
        ) -> LLMChessMove:
        print(
            f"Calling LLM with system prompt: {system_prompt}\n\n"
            f"User prompt: {user_prompt}\n\n"
            f"Response format: {LLMChessMove}"
        )
        response = self.client.responses.parse(
            model=model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            text_format=LLMChessMove,
            temperature=temperature,
        )
        print("OpenAI call successful")

        print("Extracting Pydantic object from OpenAI response...")
        output_message = next(
            item
            for item in response.output
            if isinstance(item, ParsedResponseOutputMessage)
        )
        data = output_message.content[0].parsed
        print(f"Pydantic object extracted from OpenAI response: {data}")
        return data

    def make_llm_move(self, position: str, error_message: str | None) -> LLMChessMove:
        """
        Get a move from the LLM. Returns the full LLMChessMove object with move and reasoning.
        """
        if error_message:
            formatted_user_prompt = USER_PROMPT_WITH_ERROR.format(position=position, memory=self.memory, error_message=error_message)
        else:
            formatted_user_prompt = USER_PROMPT.format(position=position, memory=self.memory)
        
        response = self.call_llm(
            model="gpt-4o",
            system_prompt=SYSTEM_PROMPT,
            user_prompt=formatted_user_prompt,
        )

        if self.memory == "":
            memory_addition = f"{response.move}: {response.reasoning}"
        else:
            memory_addition = f"\n{response.move}: {response.reasoning}"

        print(f"New memory formed: {memory_addition}")
        self.memory += memory_addition
        print("Added new memory to existing memory.")

        return response
