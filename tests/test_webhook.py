import json
from pathlib import Path

from fastapi.testclient import TestClient
from httpx import Response

from app.delivery_store import DeliveryStore
from app.security import build_signature


def signed_request(
    client: TestClient,
    *,
    body: bytes,
    delivery_id: str | None = "delivery-123",
) -> Response:
    headers = {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": build_signature("test-secret", body),
        "X-GitHub-Event": "pull_request",
    }
    if delivery_id is not None:
        headers["X-GitHub-Delivery"] = delivery_id

    return client.post(
        "/webhooks/github",
        content=body,
        headers=headers,
    )


def test_webhook_accepts_valid_signature(client: TestClient) -> None:
    payload = {"action": "opened", "pull_request": {"number": 42}}
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")

    response = signed_request(client, body=body)

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
            "X-GitHub-Delivery": "delivery-invalid",
        },
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid webhook signature"}


def test_webhook_rejects_missing_signature(client: TestClient) -> None:
    response = client.post(
        "/webhooks/github",
        json={"action": "opened"},
        headers={"X-GitHub-Delivery": "delivery-unsigned"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid webhook signature"}


def test_webhook_rejects_missing_delivery_id(client: TestClient) -> None:
    body = b'{"action":"opened"}'

    response = signed_request(client, body=body, delivery_id=None)

    assert response.status_code == 400
    assert response.json() == {"detail": "Missing X-GitHub-Delivery header"}


def test_webhook_treats_repeated_delivery_as_duplicate(
    client: TestClient,
    database_path: Path,
) -> None:
    body = b'{"action":"opened"}'
    delivery_id = "delivery-duplicate"

    first_response = signed_request(
        client,
        body=body,
        delivery_id=delivery_id,
    )
    second_response = signed_request(
        client,
        body=body,
        delivery_id=delivery_id,
    )

    assert first_response.status_code == 202
    assert first_response.json()["status"] == "accepted"
    assert second_response.status_code == 202
    assert second_response.json()["status"] == "duplicate"

    store = DeliveryStore(database_path)
    assert store.count_delivery(delivery_id) == 1