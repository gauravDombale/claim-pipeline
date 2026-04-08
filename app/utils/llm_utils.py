import json
import os
from typing import Optional
from openai import OpenAI

# Lazy client — instantiated on first use so load_dotenv() in main.py
# has already populated the environment before the key is read.
_client: Optional[OpenAI] = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. "
                "Create a .env file from .env.example and add your key."
            )
        _client = OpenAI(api_key=api_key)
    return _client


def vision_call(system_prompt: str, user_prompt: str, images_b64: list[str]) -> dict:
    """
    Send one or more base64 PNG images to GPT-4o with a prompt.
    Returns parsed JSON dict from the model's response.

    All agents use this helper — it handles the image message format
    and JSON parsing in one place.
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

    response = _get_client().chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )

    raw = response.choices[0].message.content
    return json.loads(raw)


def vision_call_single(system_prompt: str, user_prompt: str, b64_image: str) -> dict:
    """Convenience wrapper for a single image."""
    return vision_call(system_prompt, user_prompt, [b64_image])
