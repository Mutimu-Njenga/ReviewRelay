import os


def get_webhook_secret() -> str:
    """Return the configured GitHub webhook secret.

    The secret is read at request time so tests and local development can
    change the environment without restarting the Python interpreter.
    """
    secret = os.getenv("GITHUB_WEBHOOK_SECRET")
    if not secret:
        raise RuntimeError("GITHUB_WEBHOOK_SECRET is not configured")
    return secret
