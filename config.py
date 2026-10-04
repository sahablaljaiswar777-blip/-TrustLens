"""Application configuration and input limits."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Defaults suitable for local use; override with environment variables."""

    SECRET_KEY = os.environ.get("TRUSTLENS_SECRET_KEY", "local-development-key-change-before-deployment")
    DATABASE_PATH = os.environ.get("TRUSTLENS_DATABASE", str(BASE_DIR / "instance" / "trustlens.sqlite3"))
    MAX_CONTENT_LENGTH = 64 * 1024
    MAX_FIELD_LENGTH = 4000
    MAX_URL_LENGTH = 2048
    TESTING = False

