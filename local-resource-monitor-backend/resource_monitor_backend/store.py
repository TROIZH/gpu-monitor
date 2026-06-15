from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import json
import os
import sqlite3
import threading
from typing import Any, Iterator

from .timeutils import parse_range_seconds, utc_now


class ResourceStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._lock = threading.RLock()
        parent = os.path.dirname(os.path.abspath(db_path))
        os.makedirs(parent, exist_ok=True)
        self.migrate()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def migrate(self) -> None:
        with self._lock, self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS metric_samples (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    payload TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_metric_samples_timestamp
                    ON metric_samples(timestamp);

                CREATE TABLE IF NOT EXISTS process_samples (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    payload TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_process_samples_timestamp
                    ON process_samples(timestamp);

                CREATE TABLE IF NOT EXISTS bottleneck_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    payload TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_bottleneck_events_timestamp
                    ON bottleneck_events(timestamp);

                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    payload TEXT NOT NULL
                );
                """
            )

    def save_sample(self, metrics: dict[str, Any], processes: list[dict[str, Any]], event: dict[str, Any]) -> None:
        timestamp = metrics.get("timestamp") or utc_now().isoformat()
        with self._lock, self.connect() as connection:
            connection.execute(
                "INSERT INTO metric_samples (timestamp, payload) VALUES (?, ?)",
                (timestamp, self._json_dumps(metrics)),
            )
            connection.execute(
                "INSERT INTO process_samples (timestamp, payload) VALUES (?, ?)",
                (timestamp, self._json_dumps(processes)),
            )
            connection.execute(
                "INSERT INTO bottleneck_events (timestamp, type, severity, payload) VALUES (?, ?, ?, ?)",
                (
                    timestamp,
                    event.get("type") or "unknown",
                    event.get("severity") or "unknown",
                    self._json_dumps(event),
                ),
            )

    def get_latest_metric(self) -> dict[str, Any] | None:
        with self._lock, self.connect() as connection:
            row = connection.execute(
                "SELECT payload FROM metric_samples ORDER BY timestamp DESC, id DESC LIMIT 1"
            ).fetchone()
        return json.loads(row["payload"]) if row else None

    def get_latest_processes(self) -> list[dict[str, Any]]:
        with self._lock, self.connect() as connection:
            row = connection.execute(
                "SELECT payload FROM process_samples ORDER BY timestamp DESC, id DESC LIMIT 1"
            ).fetchone()
        return json.loads(row["payload"]) if row else []

    def get_latest_event(self) -> dict[str, Any] | None:
        with self._lock, self.connect() as connection:
            row = connection.execute(
                "SELECT payload FROM bottleneck_events ORDER BY timestamp DESC, id DESC LIMIT 1"
            ).fetchone()
        return json.loads(row["payload"]) if row else None

    def get_metrics_history(self, range_value: str | None = None) -> list[dict[str, Any]]:
        since = self._since_iso(parse_range_seconds(range_value, 60 * 60))
        return self.get_metrics_since(since)

    def get_metrics_since(self, since: str) -> list[dict[str, Any]]:
        with self._lock, self.connect() as connection:
            rows = connection.execute(
                "SELECT payload FROM metric_samples WHERE timestamp >= ? ORDER BY timestamp ASC",
                (since,),
            ).fetchall()
        return [json.loads(row["payload"]) for row in rows]

    def get_events_history(self, range_value: str | None = None) -> list[dict[str, Any]]:
        since = self._since_iso(parse_range_seconds(range_value, 24 * 60 * 60))
        return self.get_events_since(since)

    def get_events_since(self, since: str) -> list[dict[str, Any]]:
        with self._lock, self.connect() as connection:
            rows = connection.execute(
                "SELECT payload FROM bottleneck_events WHERE timestamp >= ? ORDER BY timestamp ASC",
                (since,),
            ).fetchall()
        return [json.loads(row["payload"]) for row in rows]

    def save_feedback(self, payload: dict[str, Any]) -> None:
        with self._lock, self.connect() as connection:
            connection.execute(
                "INSERT INTO feedback (timestamp, payload) VALUES (?, ?)",
                (utc_now().isoformat(), self._json_dumps(payload)),
            )

    def purge_old(self, raw_retention_hours: int, event_retention_days: int) -> dict[str, int]:
        sample_cutoff = (utc_now() - timedelta(hours=raw_retention_hours)).isoformat()
        event_cutoff = (utc_now() - timedelta(days=event_retention_days)).isoformat()
        deleted = {}
        with self._lock, self.connect() as connection:
            for table in ("metric_samples", "process_samples"):
                cursor = connection.execute(f"DELETE FROM {table} WHERE timestamp < ?", (sample_cutoff,))
                deleted[table] = cursor.rowcount
            cursor = connection.execute("DELETE FROM bottleneck_events WHERE timestamp < ?", (event_cutoff,))
            deleted["bottleneck_events"] = cursor.rowcount
        return deleted

    def _since_iso(self, seconds: int) -> str:
        return (datetime.now(timezone.utc) - timedelta(seconds=seconds)).isoformat().replace("+00:00", "Z")

    def _json_dumps(self, payload: Any) -> str:
        return json.dumps(self._clean_for_json(payload), ensure_ascii=False)

    def _clean_for_json(self, value: Any) -> Any:
        if isinstance(value, str):
            return value.encode("utf-8", errors="replace").decode("utf-8")
        if isinstance(value, list):
            return [self._clean_for_json(item) for item in value]
        if isinstance(value, tuple):
            return [self._clean_for_json(item) for item in value]
        if isinstance(value, dict):
            return {
                self._clean_for_json(key): self._clean_for_json(item)
                for key, item in value.items()
            }
        return value
