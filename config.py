import os
from pathlib import Path

from dotenv import load_dotenv

# --------------------------------------------------
# Load .env
# --------------------------------------------------

load_dotenv()

# --------------------------------------------------
# Directories
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

LOG_DIR = BASE_DIR / "logs"
TEMP_DIR = BASE_DIR / "temp"

LOG_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# --------------------------------------------------
# Telegram
# --------------------------------------------------

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()

# --------------------------------------------------
# LLM Provider
# --------------------------------------------------

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower().strip()

# --------------------------------------------------
# OpenAI
# --------------------------------------------------

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5"
)

# --------------------------------------------------
# Gemini
# --------------------------------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)

# --------------------------------------------------
# Server
# --------------------------------------------------

PORT = int(os.getenv("PORT", 8000))

LOG_BASE_URL = os.getenv(
    "LOG_BASE_URL",
    f"http://localhost:{PORT}/logs"
).rstrip("/")

LOG_URL = os.getenv(
    "LOG_URL",
    "https://srik-21f3002510.github.io/telegram-data-analyst/logs/run.jsonl"
)
# --------------------------------------------------
# Validation
# --------------------------------------------------

if not TELEGRAM_TOKEN:
    raise RuntimeError(
        "TELEGRAM_TOKEN not configured."
    )

if LLM_PROVIDER not in ("openai", "gemini"):
    raise RuntimeError(
        "LLM_PROVIDER must be either 'openai' or 'gemini'."
    )

if LLM_PROVIDER == "openai" and not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY missing."
    )

if LLM_PROVIDER == "gemini" and not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY missing."
    )
