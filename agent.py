"""
agent.py

Main data-analysis agent.

Responsibilities:
- Manage LLM interaction
- Register analysis tools
- Maintain reasoning loop
- Produce structured final response
"""

from typing import Any

from pydantic import BaseModel

from memory import memory
from tools import (
    download_file,
    load_dataframe,
    load_html_tables,
    sql,
)

from llm import ask_json

from config import LOG_URL

from logger import log_agent_response



class AgentResponse(BaseModel):
    answer: Any
    log_url: str


SYSTEM_PROMPT = """
You are a professional data analyst.

Your job:

1. Understand the user's data-analysis question.
2. Locate required public datasets if needed.
3. Perform calculations using Python tools.
4. Return ONLY the requested answer structure.

Rules:
- Never invent data.
- Use actual computation.
- Preserve the JSON structure requested by the user.
- Do not add explanations outside JSON.
- You must return ONLY valid JSON.
- Do not use markdown.
- Do not use ```json fences.
- Do not add explanations before or after the JSON.
"""


def run_agent(
    user_id: str,
    question: str,
):
    """
    Main entry point.
    """

    # Store conversation

    memory.add_message(
        user_id,
        "user",
        question,
    )


    history = memory.formatted_history(
        user_id
    )


    prompt = f"""
Conversation history:

{history}


Current question:

{question}
"""


    result = ask_json(
        SYSTEM_PROMPT,
        prompt,
    )

    result["log_url"] = LOG_URL


    memory.add_message(
        user_id,
        "assistant",
        str(result),
    )

    log_agent_response(result)

    return result
