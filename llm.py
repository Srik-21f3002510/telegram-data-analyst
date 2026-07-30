"""
Unified LLM interface.

Supports:

- Google Gemini
- OpenAI

Usage:

from llm import ask_llm

answer = ask_llm(
    system_prompt="You are a data analyst.",
    user_prompt="What is 2+2?"
)
"""

from __future__ import annotations

import json
import time
from typing import Any, Optional

from config import (
    LLM_PROVIDER,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)

# ---------------------------------------------------
# OpenAI
# ---------------------------------------------------

if LLM_PROVIDER == "openai":
    from openai import OpenAI

    openai_client = OpenAI(
        api_key=OPENAI_API_KEY
    )

# ---------------------------------------------------
# Gemini
# ---------------------------------------------------

if LLM_PROVIDER == "gemini":
    from google import genai

    gemini_client = genai.Client(
        api_key=GEMINI_API_KEY
    )


# ---------------------------------------------------
# Internal Providers
# ---------------------------------------------------

def _ask_openai(
    system_prompt: str,
    user_prompt: str,
    temperature: float,
) -> str:

    response = openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=temperature,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    )

    return response.choices[0].message.content.strip()


def _ask_gemini(
    system_prompt: str,
    user_prompt: str,
    temperature: float,
) -> str:

    prompt = f"""
SYSTEM:

{system_prompt}

-----------------------

USER:

{user_prompt}
"""

    response = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config={
            "temperature": temperature,
        },
    )

    return response.text.strip()


# ---------------------------------------------------
# Public API
# ---------------------------------------------------

def ask_llm(
    system_prompt: str,
    user_prompt: str,
    *,
    temperature: float = 0.0,
    retries: int = 3,
) -> str:
    """
    Returns plain text.

    Automatically retries transient failures.
    """

    last_error = None

    for attempt in range(retries):

        try:

            if LLM_PROVIDER == "openai":

                return _ask_openai(
                    system_prompt,
                    user_prompt,
                    temperature,
                )

            elif LLM_PROVIDER == "gemini":

                return _ask_gemini(
                    system_prompt,
                    user_prompt,
                    temperature,
                )

            raise RuntimeError(
                f"Unknown provider {LLM_PROVIDER}"
            )

        except Exception as exc:

            last_error = exc

            if attempt < retries - 1:

                time.sleep(2)

    raise RuntimeError(last_error)


# ---------------------------------------------------
# JSON helper
# ---------------------------------------------------

import re
import json


def clean_json(text: str) -> str:
    """
    Remove markdown code fences and extract JSON.
    """

    text = text.strip()

    # Remove ```json and ```
    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^```\s*",
        "",
        text
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    return text.strip()


def ask_json(
    system_prompt: str,
    user_prompt: str,
) -> dict[str, Any]:
    """
    Forces the model to return valid JSON.
    """

    prompt = (
        user_prompt
        + "\n\n"
        + "Return ONLY valid JSON."
    )

    text = ask_llm(
        system_prompt,
        prompt,
        temperature=0,
    )

    try:

        cleaned = clean_json(text)
        
        return json.loads(cleaned)

    except Exception as exc:

        raise RuntimeError(
            f"Model returned invalid JSON:\n\n{text}"
        ) from exc


# ---------------------------------------------------
# Simple health check
# ---------------------------------------------------

def health_check() -> bool:

    try:

        answer = ask_llm(
            "You are a helpful assistant.",
            "Reply with OK",
        )

        return bool(answer)

    except Exception:

        return False
