import os
from typing import Optional, Type, TypeVar
from pydantic import BaseModel
from openai import AsyncOpenAI

# Lazy client — instantiated on first use so load_dotenv() in main.py
# has already populated the environment before the key is read.
_client: Optional[AsyncOpenAI] = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. "
                "Create a .env file from .env.example and add your key."
            )
        _client = AsyncOpenAI(api_key=api_key)
    return _client


T = TypeVar("T", bound=BaseModel)


async def vision_call(system_prompt: str, user_prompt: str, images_b64: list[str], response_model: Type[T]) -> T:
    """
    Send one or more base64 PNG images to GPT-4o with a prompt.
    Uses OpenAI's native Structured Outputs via `.parse()` to guarantee
    the response strictly matches the provided Pydantic `response_model`.
    """
    content = [{"type": "text", "text": user_prompt}]

    for b64 in images_b64:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{b64}",
                "detail": "high",
            },
        })

    client = _get_client()
    response = await client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",  # Support for Structured Outputs via math model format
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ],
        response_format=response_model,
        temperature=0,
    )

    result = response.choices[0].message.parsed
    if result is None:
        raise ValueError("Model failed to parse structured output properly.")
    return result


async def vision_call_single(system_prompt: str, user_prompt: str, b64_image: str, response_model: Type[T]) -> T:
    """Convenience wrapper for a single image."""
    return await vision_call(system_prompt, user_prompt, [b64_image], response_model)
