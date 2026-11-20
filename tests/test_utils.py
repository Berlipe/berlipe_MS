"""Utility and formatter tests."""

from app.utils.formatters import format_ms, format_mbps, format_bytes, format_percent


def test_format_ms():
    assert format_ms(None) == "—"
    assert format_ms(12.345, precision=1) == "12.3 ms"


def test_format_mbps():
    assert format_mbps(None) == "—"
    assert format_mbps(100.5) == "100.50 Mbps"


def test_format_bytes():
    assert format_bytes(500) == "500 B"
    assert "KB" in format_bytes(2048)


def test_format_percent():
    assert format_percent(None) == "—"
    assert format_percent(3.14) == "3.1 %"
