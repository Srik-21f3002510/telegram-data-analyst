"""
logger.py

Creates JSONL execution logs.

Each run creates entries like:

{
    "timestamp": "...",
    "event": "user_message",
    "data": {...}
}

The resulting file can be hosted publicly and returned as:

{
    "answer": ...,
    "log_url": "https://your-host/run.jsonl"
}
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import LOG_DIR, LOG_BASE_URL


# --------------------------------------------------
# Current run
# --------------------------------------------------

RUN_ID = uuid.uuid4().hex

LOG_FILE = LOG_DIR / "run.jsonl"


# --------------------------------------------------
# Internal helpers
# --------------------------------------------------

def _timestamp() -> str:
    """
    UTC timestamp.
    """

    return datetime.now(
        timezone.utc
    ).isoformat()



def _write(
    event: str,
    data: dict[str, Any],
):
    """
    Append one JSON object to JSONL file.
    """

    record = {
        "timestamp": _timestamp(),
        "run_id": RUN_ID,
        "event": event,
        "data": data,
    }


    with open(
        LOG_FILE,
        "a",
        encoding="utf-8",
    ) as file:

        file.write(
            json.dumps(
                record,
                ensure_ascii=False,
            )
            + "\n"
        )



# --------------------------------------------------
# Public logging functions
# --------------------------------------------------

def log_user_message(
    user_id: str,
    message: str,
):
    """
    Record Telegram input.
    """

    _write(
        "user_message",
        {
            "user_id": str(user_id),
            "message": message,
        },
    )



def log_llm_request(
    provider: str,
    model: str,
    prompt: str,
):
    """
    Record LLM request.
    """

    _write(
        "llm_request",
        {
            "provider": provider,
            "model": model,
            "prompt": prompt,
        },
    )



def log_llm_response(
    response: str,
):
    """
    Record LLM output.
    """

    _write(
        "llm_response",
        {
            "response": response,
        },
    )



def log_tool_call(
    tool_name: str,
    arguments: dict[str, Any],
    result: Any,
):
    """
    Record tool execution.
    """

    _write(
        "tool_call",
        {
            "tool": tool_name,
            "arguments": arguments,
            "result": str(result),
        },
    )



def log_error(
    error: Exception,
):
    """
    Record failures.
    """

    _write(
        "error",
        {
            "type": type(error).__name__,
            "message": str(error),
        },
    )



def log_final_answer(
    answer: Any,
):
    """
    Record final JSON answer.
    """

    _write(
        "final_answer",
        {
            "answer": answer,
        },
    )


# --------------------------------------------------
# Public URL
# --------------------------------------------------

def get_log_url() -> str:
    """
    Returns public URL of JSONL log.

    Example:

    https://example.com/logs/run.jsonl
    """

    return (
        f"{LOG_BASE_URL}/run.jsonl"
    )
