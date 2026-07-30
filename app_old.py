"""
app.py

Telegram bot entry point.

Flow:

Telegram
   |
   | message
   v
Agent
   |
   | JSON
   v
Telegram reply
"""

from __future__ import annotations

import json
import traceback

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
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
# Telegram message handler
# --------------------------------------------------

async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not update.message:
        return


    user_id = str(
        update.message.from_user.id
    )

    question = (
        update.message.text
        or ""
    ).strip()


    if not question:
        return


    # -------------------------------
    # Log incoming question
    # -------------------------------

    log_user_message(
        user_id,
        question,
    )


    try:

        # ---------------------------
        # Run data analyst agent
        # ---------------------------

        result = run_agent(
            user_id=user_id,
            question=question,
        )


        # ---------------------------
        # Required output format
        # ---------------------------

        response = json.dumps(
            result,
            ensure_ascii=False,
        )


        # Telegram message must contain
        # ONLY JSON

        await update.message.reply_text(
            response
        )


    except Exception as exc:

        log_error(exc)

        traceback.print_exc()


        # Even errors should follow
        # required JSON structure

        error_response = {

            "answer": {
                "error": str(exc)
            },

            "log_url":
                "ERROR"
        }


        await update.message.reply_text(
            json.dumps(
                error_response,
                ensure_ascii=False,
            )
        )


# --------------------------------------------------
# Health command
# --------------------------------------------------

async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    await update.message.reply_text(
        json.dumps(
            {
                "answer": {
                    "status": "running"
                },

                "log_url": ""
            }
        )
    )


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    application = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .build()
    )


    application.add_handler(
        MessageHandler(
            filters.COMMAND & filters.Regex("^/start$"),
            start_command,
        )
    )


    application.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            handle_message,
        )
    )


    print(
        "Telegram data analyst bot running..."
    )


    application.run_polling()



if __name__ == "__main__":

    main()
