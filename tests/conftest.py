from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def database_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> Path:
    path = tmp_path / "reviewrelay-test.db"
    monkeypatch.setenv("REVIEWRELAY_DB_PATH", str(path))
    return path


@pytest.fixture(autouse=True)
def test_environment(
    monkeypatch: pytest.MonkeyPatch,
    database_path: Path,
) -> None:
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "test-secret")


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)