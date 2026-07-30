"""
app.py

Telegram Data Analyst Bot

Flow:

Telegram
    |
    v
app.py
    |
    v
agent.py
    |
    v
LLM + Data Tools
    |
    v
JSON response
"""

from __future__ import annotations

import json
import logging
import traceback


from telegram import Update

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


from config import TELEGRAM_TOKEN

from agent import run_agent

from logger import (
    log_user_message,
    log_error,
)


# --------------------------------------------------
# Logging configuration
# --------------------------------------------------

logging.basicConfig(
    format=(
        "%(asctime)s - "
        "%(name)s - "
        "%(levelname)s - "
        "%(message)s"
    ),
    level=logging.INFO,
)


logging.getLogger(
    "httpx"
).setLevel(
    logging.WARNING
)


# --------------------------------------------------
# Startup callback
# --------------------------------------------------

async def startup(application):

    print(
        "Polling started successfully"
    )


# --------------------------------------------------
# /start command
# --------------------------------------------------

async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    user_id = (
        update.message
        .from_user
        .id
    )

    print(
        "START received from:",
        user_id
    )


    response = {

        "answer": {
            "status": "running"
        },

        "log_url": ""
    }


    await update.message.reply_text(
        json.dumps(
            response,
            ensure_ascii=False
        )
    )


# --------------------------------------------------
# Text messages
# --------------------------------------------------

async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not update.message:
        return


    user_id = str(
        update.message
        .from_user
        .id
    )


    question = (
        update.message.text
        or ""
    ).strip()


    print(
        "MESSAGE received:",
        question
    )


    if not question:
        return


    try:

        # Save incoming message

        log_user_message(
            user_id,
            question
        )


        # Run analyst agent

        result = run_agent(
            user_id=user_id,
            question=question,
        )


        # IMPORTANT:
        # Telegram response must be
        # exactly one JSON object

        response = json.dumps(
            result,
            ensure_ascii=False
        )


        await update.message.reply_text(
            response
        )


    except Exception as exc:

        print(
            "ERROR:",
            exc
        )

        traceback.print_exc()


        log_error(
            exc
        )


        error_response = {

            "answer": {
                "error": str(exc)
            },

            "log_url": ""
        }


        await update.message.reply_text(
            json.dumps(
                error_response,
                ensure_ascii=False
            )
        )


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print(
    "Using token ending:",
    TELEGRAM_TOKEN[-10:]
    )

    application = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .post_init(startup)
        .build()
    )


    # /start handler

    application.add_handler(
        CommandHandler(
            "start",
            start_command
        )
    )


    # Normal text messages

    application.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            handle_message
        )
    )


    print(
        "Telegram data analyst bot running..."
    )


    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )


# --------------------------------------------------
# Entry point
# --------------------------------------------------

if __name__ == "__main__":

    main()
