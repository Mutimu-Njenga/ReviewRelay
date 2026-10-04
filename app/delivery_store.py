import hashlib
import sqlite3
from pathlib import Path


class DeliveryStore:
    """Persist GitHub delivery IDs and reject duplicate processing."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS webhook_deliveries (
                    delivery_id TEXT PRIMARY KEY,
                    event TEXT,
                    payload_sha256 TEXT NOT NULL,
                    received_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def record_delivery(
        self,
        delivery_id: str,
        event: str | None,
        body: bytes,
    ) -> bool:
        """Return True for a newly stored delivery and False for a duplicate."""
        payload_sha256 = hashlib.sha256(body).hexdigest()

        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO webhook_deliveries (
                        delivery_id,
                        event,
                        payload_sha256
                    ) VALUES (?, ?, ?)
                    """,
                    (delivery_id, event, payload_sha256),
                )
        except sqlite3.IntegrityError:
            return False

        return True

    def count_delivery(self, delivery_id: str) -> int:
        """Return the number of records for one delivery ID."""
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS count
                FROM webhook_deliveries
                WHERE delivery_id = ?
                """,
                (delivery_id,),
            ).fetchone()

        return int(row["count"])