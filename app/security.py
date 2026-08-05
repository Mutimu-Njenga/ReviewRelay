import hashlib
import hmac


SIGNATURE_PREFIX = "sha256="


def build_signature(secret: str, body: bytes) -> str:
    """Create the GitHub-compatible SHA-256 HMAC signature."""
    digest = hmac.new(
        secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()
    return f"{SIGNATURE_PREFIX}{digest}"


def verify_signature(secret: str, body: bytes, supplied_signature: str | None) -> bool:
    """Validate a GitHub X-Hub-Signature-256 header safely."""
    if not supplied_signature or not supplied_signature.startswith(SIGNATURE_PREFIX):
        return False

    expected_signature = build_signature(secret, body)
    return hmac.compare_digest(expected_signature, supplied_signature)
