"""Unit tests for ping statistics."""

from app.network.ping import (
    calculate_jitter,
    calculate_packet_loss,
    summarize_ping,
    PingResult,
)


def test_calculate_jitter_empty():
    assert calculate_jitter([]) == 0.0
    assert calculate_jitter([10.0]) == 0.0


def test_calculate_jitter_basic():
    # |20-10|=10, |15-20|=5 → avg 7.5
    assert calculate_jitter([10.0, 20.0, 15.0]) == 7.5


def test_calculate_packet_loss():
    results = [
        PingResult(target="x", success=True, latency_ms=10),
        PingResult(target="x", success=False, error="timeout"),
        PingResult(target="x", success=True, latency_ms=12),
        PingResult(target="x", success=False, error="timeout"),
    ]
    assert calculate_packet_loss(results) == 50.0
    assert calculate_packet_loss([]) == 0.0


def test_summarize_ping():
    results = [
        PingResult(target="8.8.8.8", success=True, latency_ms=10.0),
        PingResult(target="8.8.8.8", success=True, latency_ms=20.0),
        PingResult(target="8.8.8.8", success=False, error="timeout"),
    ]
    s = summarize_ping(results)
    assert s["count"] == 3
    assert s["success_count"] == 2
    assert s["packet_loss_pct"] == 33.3
    assert s["min_ms"] == 10.0
    assert s["max_ms"] == 20.0
    assert s["avg_ms"] == 15.0
    assert s["jitter_ms"] == 10.0
