from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.security import build_signature, verify_signature


@pytest.mark.parametrize(
    "supplied_signature",
    ["sha256=\u00e9", "sha256=" + "0" * 63 + "\u00e9", "sha256=\u200b" + "0" * 64],
)
def test_non_ascii_signature_is_rejected_without_raising(
    supplied_signature: str,
) -> None:
    assert verify_signature("test-secret", b"{}", supplied_signature) is False


def test_valid_ascii_signature_remains_accepted() -> None:
    # Independently calculated SHA-256 HMAC for the stated synthetic bytes/key.
    signature = "sha256=7bea5b1ceb5bdece16513861ce0b365520067ee398993187b6db3fc709aa05c9"
    assert verify_signature("synthetic-secret", b"{}", signature) is True


def test_non_ascii_payload_bytes_remain_valid() -> None:
    body = '{"label":"caf\u00e9"}'.encode("utf-8")
    signature = build_signature("test-secret", body)
    assert signature.isascii()
    assert verify_signature("test-secret", body, signature) is True


@pytest.mark.parametrize(
    "header",
    [b"sha256=\xe9", b"sha256=" + b"0" * 63 + b"\xe9"],
)
def test_endpoint_rejects_non_ascii_header_before_persistence(
    client: TestClient, database_path: Path, header: bytes
) -> None:
    response = client.post(
        "/webhooks/github",
        content=b"{}",
        headers=[
            (b"X-Hub-Signature-256", header),
            (b"X-GitHub-Delivery", b"malformed-header-test"),
        ],
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid webhook signature"}
    assert not database_path.exists()
