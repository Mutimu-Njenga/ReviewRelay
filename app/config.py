import os
from pathlib import Path


def get_webhook_secret() -> str:
    """Return the configured GitHub webhook secret."""
    secret = os.getenv("GITHUB_WEBHOOK_SECRET")
    if not secret:
        raise RuntimeError("GITHUB_WEBHOOK_SECRET is not configured")
    return secret


def get_delivery_database_path() -> Path:
    """Return the SQLite path used to persist webhook delivery IDs."""
    return Path(os.getenv("REVIEWRELAY_DB_PATH", "reviewrelay.db"))