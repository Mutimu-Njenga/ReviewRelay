import json

from fastapi.testclient import TestClient

from app.security import build_signature


def test_webhook_accepts_valid_signature(client: TestClient) -> None:
    payload = {"action": "opened", "pull_request": {"number": 42}}
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    signature = build_signature("test-secret", body)

    response = client.post(
        "/webhooks/github",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": signature,
            "X-GitHub-Event": "pull_request",
            "X-GitHub-Delivery": "delivery-123",
        },
    )

    assert response.status_code == 202
    assert response.json() == {
        "status": "accepted",
        "event": "pull_request",
        "delivery": "delivery-123",
    }


def test_webhook_rejects_invalid_signature(client: TestClient) -> None:
    body = b'{"action":"opened"}'

    response = client.post(
        "/webhooks/github",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": "sha256=incorrect",
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid webhook signature"}


def test_webhook_rejects_missing_signature(client: TestClient) -> None:
    response = client.post(
        "/webhooks/github",
        json={"action": "opened"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid webhook signature"}
