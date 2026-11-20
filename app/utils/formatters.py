"""Display helpers."""

from __future__ import annotations

from datetime import datetime
from typing import Optional


def format_ms(value: Optional[float], precision: int = 1) -> str:
    if value is None:
        return "—"
    return f"{value:.{precision}f} ms"


def format_mbps(value: Optional[float], precision: int = 2) -> str:
    if value is None:
        return "—"
    return f"{value:.{precision}f} Mbps"


def format_bytes(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    for unit in ("KB", "MB", "GB", "TB"):
        n /= 1024.0
        if n < 1024:
            return f"{n:.1f} {unit}"
    return f"{n:.1f} PB"


def format_timestamp(ts: float, fmt: str = "%d/%m/%Y %H:%M:%S") -> str:
    try:
        return datetime.fromtimestamp(ts).strftime(fmt)
    except (OSError, ValueError, OverflowError):
        return "—"


def format_percent(value: Optional[float], precision: int = 1) -> str:
    if value is None:
        return "—"
    return f"{value:.{precision}f} %"
