import os
from dotenv import load_dotenv
import logging

from openai import OpenAI
from openai.types.responses.parsed_response import (
    ParsedResponse,
    ParsedResponseOutputMessage,
)

# Configure logging for OpenAI
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

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
            response_format,
            temperature: float = 1,
        ):
        print(
            f"Calling LLM with system prompt: {system_prompt}\n\n"
            f"User prompt: {user_prompt}\n\n"
            f"Response format: {response_format}"
        )
        response = self.client.responses.parse(
            model=model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            text_format=response_format,
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

