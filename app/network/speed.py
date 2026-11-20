"""Lightweight download/upload speed estimation.

Uses small HTTP transfers to public endpoints.
This is an approximation, not a full speedtest.net equivalent.
"""

from __future__ import annotations

import time
import urllib.request
from dataclasses import dataclass
from typing import Optional


@dataclass
class SpeedResult:
    success: bool
    mbps: Optional[float] = None
    bytes_transferred: int = 0
    duration_sec: float = 0.0
    error: Optional[str] = None


# Small public files for download test (Cloudflare, Google, etc.)
DOWNLOAD_URLS = [
    "https://speed.cloudflare.com/__down?bytes=1000000",  # ~1 MB
    "https://proof.ovh.net/files/1Mb.dat",
]

# For upload we POST a small payload to a discard endpoint if available,
# otherwise we approximate with a local measurement note.
UPLOAD_TEST_SIZE = 256 * 1024  # 256 KB


def estimate_download_speed(timeout: float = 12.0) -> SpeedResult:
    """
    Download a small file and measure throughput.
    Returns Mbps (megabits per second).
    """
    last_error = None
    for url in DOWNLOAD_URLS:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "berlip_MS/1.0"},
            )
            start = time.perf_counter()
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
            elapsed = time.perf_counter() - start
            if elapsed <= 0:
                continue
            size = len(data)
            # Mbps = (bytes * 8) / seconds / 1_000_000
            mbps = (size * 8) / elapsed / 1_000_000
            return SpeedResult(
                success=True,
                mbps=round(mbps, 2),
                bytes_transferred=size,
                duration_sec=round(elapsed, 3),
            )
        except Exception as e:
            last_error = str(e)
            continue
    return SpeedResult(success=False, error=last_error or "all_endpoints_failed")


def estimate_upload_speed(timeout: float = 12.0) -> SpeedResult:
    """
    Approximate upload speed by POSTing data to a public echo/discard endpoint.
    Falls back to a conservative estimate message if no suitable endpoint works.
    """
    # Cloudflare has an upload endpoint used by their speed test
    url = "https://speed.cloudflare.com/__up"
    payload = b"0" * UPLOAD_TEST_SIZE
    try:
        req = urllib.request.Request(
            url,
            data=payload,
            method="POST",
            headers={
                "User-Agent": "berlip_MS/1.0",
                "Content-Type": "application/octet-stream",
            },
        )
        start = time.perf_counter()
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            _ = resp.read()
        elapsed = time.perf_counter() - start
        if elapsed <= 0:
            return SpeedResult(success=False, error="zero_duration")
        mbps = (len(payload) * 8) / elapsed / 1_000_000
        return SpeedResult(
            success=True,
            mbps=round(mbps, 2),
            bytes_transferred=len(payload),
            duration_sec=round(elapsed, 3),
        )
    except Exception as e:
        return SpeedResult(success=False, error=str(e))
