"""SQLite persistence for measurement history."""

from __future__ import annotations

import json
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

from app.core.config import get_config


class Database:
    def __init__(self, db_path: Optional[Path] = None) -> None:
        cfg = get_config()
        self.db_path = Path(db_path) if db_path else cfg.db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    @contextmanager
    def _conn(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(str(self.db_path), timeout=10)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_schema(self) -> None:
        with self._conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    target TEXT NOT NULL,
                    latency_ms REAL,
                    jitter_ms REAL,
                    packet_loss_pct REAL,
                    download_mbps REAL,
                    upload_mbps REAL,
                    success INTEGER NOT NULL DEFAULT 1,
                    extra TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_measurements_ts
                    ON measurements(timestamp);

                CREATE INDEX IF NOT EXISTS idx_measurements_target
                    ON measurements(target);

                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    event_type TEXT NOT NULL,
                    message TEXT,
                    details TEXT
                );
                """
            )

    def insert_measurement(
        self,
        target: str,
        latency_ms: Optional[float] = None,
        jitter_ms: Optional[float] = None,
        packet_loss_pct: Optional[float] = None,
        download_mbps: Optional[float] = None,
        upload_mbps: Optional[float] = None,
        success: bool = True,
        extra: Optional[dict] = None,
        timestamp: Optional[float] = None,
    ) -> int:
        ts = timestamp if timestamp is not None else time.time()
        extra_json = json.dumps(extra) if extra else None
        with self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO measurements
                    (timestamp, target, latency_ms, jitter_ms, packet_loss_pct,
                     download_mbps, upload_mbps, success, extra)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ts,
                    target,
                    latency_ms,
                    jitter_ms,
                    packet_loss_pct,
                    download_mbps,
                    upload_mbps,
                    1 if success else 0,
                    extra_json,
                ),
            )
            return int(cur.lastrowid)

    def query_measurements(
        self,
        start_ts: Optional[float] = None,
        end_ts: Optional[float] = None,
        target: Optional[str] = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        clauses = []
        params: list[Any] = []
        if start_ts is not None:
            clauses.append("timestamp >= ?")
            params.append(start_ts)
        if end_ts is not None:
            clauses.append("timestamp <= ?")
            params.append(end_ts)
        if target:
            clauses.append("target = ?")
            params.append(target)

        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        sql = f"""
            SELECT * FROM measurements
            {where}
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])

        with self._conn() as conn:
            rows = conn.execute(sql, params).fetchall()
            return [dict(r) for r in rows]

    def count_measurements(
        self,
        start_ts: Optional[float] = None,
        end_ts: Optional[float] = None,
    ) -> int:
        clauses = []
        params: list[Any] = []
        if start_ts is not None:
            clauses.append("timestamp >= ?")
            params.append(start_ts)
        if end_ts is not None:
            clauses.append("timestamp <= ?")
            params.append(end_ts)
        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        with self._conn() as conn:
            row = conn.execute(f"SELECT COUNT(*) AS c FROM measurements {where}", params).fetchone()
            return int(row["c"]) if row else 0

    def delete_older_than(self, days: int) -> int:
        cutoff = time.time() - (days * 86400)
        with self._conn() as conn:
            cur = conn.execute("DELETE FROM measurements WHERE timestamp < ?", (cutoff,))
            return cur.rowcount

    def clear_all(self) -> None:
        with self._conn() as conn:
            conn.execute("DELETE FROM measurements")
            conn.execute("DELETE FROM events")

    def export_csv(self, path: Path, start_ts: Optional[float] = None, end_ts: Optional[float] = None) -> int:
        rows = self.query_measurements(start_ts=start_ts, end_ts=end_ts, limit=100_000)
        import csv
        with open(path, "w", newline="", encoding="utf-8") as f:
            if not rows:
                writer = csv.writer(f)
                writer.writerow(["id", "timestamp", "target", "latency_ms", "jitter_ms",
                                 "packet_loss_pct", "download_mbps", "upload_mbps", "success"])
                return 0
            fieldnames = list(rows[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return len(rows)

    def export_json(self, path: Path, start_ts: Optional[float] = None, end_ts: Optional[float] = None) -> int:
        rows = self.query_measurements(start_ts=start_ts, end_ts=end_ts, limit=100_000)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2, ensure_ascii=False)
        return len(rows)


_db_instance: Database | None = None


def get_db() -> Database:
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
