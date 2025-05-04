import os
from dotenv import load_dotenv
import logging

# Configure logging for OpenAI
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

SYSTEM_PROMPT = """You are a grandmaster chess player.
Given the position in PGN format, return the best, valid next move in standard algebraic notation.
Example of a correct response: 'e5'
Examples of incorrect responses:
- '2. e5'
- 'e5 is the best move to play in this position.'"""

USER_PROMPT = """Position: {position}

Black to play.

For the love of god please don't add prefixes like '2.' or '2... ' to your move.

Move: """

USER_PROMPT_WITH_ERROR = """
Position: {position}

Black to play.

Make sure to avoid this error: {error_message}

For the love of god please don't add prefixes like '2.' or '2... ' to your move.

Move: """

class LLMManager():
    def __init__(self):
        load_dotenv("secrets.env")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=openai_api_key)

    def call_llm(
            self,
            model: str,
            system_prompt: str,
            user_prompt: str,
            temperature: float = 0
        ) -> str:
        print(f"Calling LLM with system prompt: {system_prompt}\n\nUser prompt: {user_prompt}")
        response: ChatCompletion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=model,
            temperature=temperature,
            # max_tokens=300
        )
        message = response.choices[0].message.content
        print(f"LLM response: {message}")
        return message

    def make_llm_move(self, position: str, error_message: str | None) -> str:

        if error_message:
            formatted_user_prompt = USER_PROMPT_WITH_ERROR.format(position=position, error_message=error_message)
        else:
            formatted_user_prompt = USER_PROMPT.format(position=position)
        
        response = self.call_llm(
            model="gpt-4o",
            system_prompt=SYSTEM_PROMPT,
            user_prompt=formatted_user_prompt
        )

        return response
