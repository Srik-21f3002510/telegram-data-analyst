"""
logger.py

JSONL logger for Telegram Data Analyst Bot.

Creates:

run.jsonl

Each line contains one JSON object.

The file is intended to be published through
GitHub Pages.

Example public URL:

https://username.github.io/repository/run.jsonl
"""

from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import LOG_BASE_URL


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

LOG_FILE = BASE_DIR / "run.jsonl"


RUN_ID = uuid.uuid4().hex


_write_lock = threading.Lock()


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def _timestamp() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()



def _safe_json(value: Any):

    try:
        json.dumps(value)
        return value

    except Exception:
        return str(value)



def _write(
    event: str,
    data: dict[str, Any]
):

    record = {

        "timestamp": _timestamp(),

        "run_id": RUN_ID,

        "event": event,

        "data": {
            k: _safe_json(v)
            for k, v in data.items()
        }
    }


    with _write_lock:

        with open(
            LOG_FILE,
            "a",
            encoding="utf-8"
        ) as f:

            f.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                )
                + "\n"
            )

            f.flush()



# --------------------------------------------------
# Public logging methods
# --------------------------------------------------

def log_user_message(
    user_id: str,
    message: str
):

    _write(
        "user_message",
        {
            "user_id": str(user_id),
            "message": message
        }
    )



def log_llm_request(
    provider: str,
    model: str,
    prompt: str
):

    _write(
        "llm_request",
        {
            "provider": provider,
            "model": model,
            "prompt": prompt
        }
    )



def log_llm_response(
    response: str
):

    _write(
        "llm_response",
        {
            "response": response
        }
    )



def log_tool_call(
    tool_name: str,
    arguments: dict[str, Any],
    result: Any
):

    _write(
        "tool_call",
        {
            "tool": tool_name,
            "arguments": arguments,
            "result": result
        }
    )



def log_final_answer(
    answer: Any
):

    _write(
        "final_answer",
        {
            "answer": answer
        }
    )



def log_error(
    error: Exception
):

    _write(
        "error",
        {
            "type": type(error).__name__,
            "message": str(error)
        }
    )



# --------------------------------------------------
# GitHub Pages URL
# --------------------------------------------------

def get_log_url() -> str:
    """
    Returns public GitHub Pages URL.

    Example:

    https://username.github.io/repo/run.jsonl
    """

    return (
        f"{LOG_BASE_URL.rstrip('/')}/run.jsonl"
    )
