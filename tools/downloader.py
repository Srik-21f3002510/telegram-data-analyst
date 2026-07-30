from __future__ import annotations

import mimetypes
import uuid
from pathlib import Path
from urllib.parse import urlparse

import requests

from config import TEMP_DIR


def download_file(url: str) -> Path:
    """
    Download a file from a public URL into TEMP_DIR.
    Returns the local Path.
    """

    response = requests.get(
        url,
        timeout=120,
        stream=True,
    )
    response.raise_for_status()

    parsed = urlparse(url)

    suffix = Path(parsed.path).suffix

    if not suffix:
        suffix = mimetypes.guess_extension(
            response.headers.get("content-type", "")
        ) or ".dat"

    filename = f"{uuid.uuid4().hex}{suffix}"

    destination = TEMP_DIR / filename

    with open(destination, "wb") as f:
        for chunk in response.iter_content(8192):
            if chunk:
                f.write(chunk)

    return destination
