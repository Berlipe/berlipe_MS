"""Database tests using temporary file."""

import time
from pathlib import Path

import pytest

from app.database.db import Database


@pytest.fixture
def db(tmp_path: Path):
    path = tmp_path / "test_history.db"
    return Database(db_path=path)


def test_insert_and_query(db: Database):
    mid = db.insert_measurement(
        target="8.8.8.8",
        latency_ms=12.5,
        jitter_ms=1.2,
        packet_loss_pct=0.0,
        success=True,
    )
    assert mid > 0
    rows = db.query_measurements(limit=10)
    assert len(rows) == 1
    assert rows[0]["target"] == "8.8.8.8"
    assert rows[0]["latency_ms"] == 12.5


def test_count_and_period(db: Database):
    now = time.time()
    db.insert_measurement(target="a", latency_ms=1, timestamp=now - 100)
    db.insert_measurement(target="b", latency_ms=2, timestamp=now)
    assert db.count_measurements() == 2
    assert db.count_measurements(start_ts=now - 50) == 1


def test_export_csv_json(db: Database, tmp_path: Path):
    db.insert_measurement(target="x", latency_ms=5.0)
    csv_path = tmp_path / "out.csv"
    json_path = tmp_path / "out.json"
    n1 = db.export_csv(csv_path)
    n2 = db.export_json(json_path)
    assert n1 == 1
    assert n2 == 1
    assert csv_path.exists()
    assert json_path.exists()
    assert "latency_ms" in csv_path.read_text(encoding="utf-8")


def test_clear(db: Database):
    db.insert_measurement(target="z", latency_ms=1)
    db.clear_all()
    assert db.count_measurements() == 0
