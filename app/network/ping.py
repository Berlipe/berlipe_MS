"""ICMP ping implementation and statistics helpers.

Uses a pure-Python approach with raw sockets when possible,
falling back to system ping command parsed safely when raw
sockets are unavailable (common on Windows without admin).
"""

from __future__ import annotations

import platform
import re
import socket
import struct
import subprocess
import time
from dataclasses import dataclass, field
from typing import List, Optional, Sequence


@dataclass
class PingResult:
    """Single or aggregated ping result."""

    target: str
    success: bool
    latency_ms: Optional[float] = None
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    ttl: Optional[int] = None
    bytes_sent: int = 32

    @property
    def ok(self) -> bool:
        return self.success and self.latency_ms is not None


def _checksum(data: bytes) -> int:
    """Calculate Internet Checksum."""
    if len(data) % 2:
        data += b"\x00"
    s = sum(struct.unpack("!%dH" % (len(data) // 2), data))
    s = (s >> 16) + (s & 0xFFFF)
    s += s >> 16
    return ~s & 0xFFFF


def _create_icmp_echo(seq: int, payload_size: int = 32) -> bytes:
    """Create ICMP Echo Request packet."""
    # Type 8, Code 0, checksum 0, id, seq
    header = struct.pack("!BBHHH", 8, 0, 0, os_getpid() & 0xFFFF, seq)
    payload = b"Q" * payload_size
    chk = _checksum(header + payload)
    header = struct.pack("!BBHHH", 8, 0, chk, os_getpid() & 0xFFFF, seq)
    return header + payload


def os_getpid() -> int:
    import os
    return os.getpid()


def ping_once_raw(target: str, timeout: float = 2.0, payload_size: int = 32) -> PingResult:
    """Attempt raw ICMP ping (requires privileges on most systems)."""
    try:
        # Resolve
        addr_info = socket.getaddrinfo(target, None, socket.AF_INET)
        dest = addr_info[0][4][0]
    except socket.gaierror as e:
        return PingResult(target=target, success=False, error=f"DNS: {e}")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        sock.settimeout(timeout)
    except PermissionError:
        return PingResult(target=target, success=False, error="raw_socket_denied")
    except OSError as e:
        return PingResult(target=target, success=False, error=str(e))

    try:
        packet = _create_icmp_echo(1, payload_size)
        start = time.perf_counter()
        sock.sendto(packet, (dest, 0))
        while True:
            data, _ = sock.recvfrom(1024)
            recv_time = time.perf_counter()
            # Skip IP header (usually 20 bytes)
            ip_header_len = (data[0] & 0x0F) * 4
            icmp = data[ip_header_len:]
            if len(icmp) < 8:
                continue
            icmp_type, code, _, pkt_id, seq = struct.unpack("!BBHHH", icmp[:8])
            if icmp_type == 0 and pkt_id == (os_getpid() & 0xFFFF):
                latency = (recv_time - start) * 1000.0
                ttl = data[8]  # TTL is in IP header
                return PingResult(
                    target=target,
                    success=True,
                    latency_ms=round(latency, 2),
                    ttl=ttl,
                    bytes_sent=payload_size,
                )
    except socket.timeout:
        return PingResult(target=target, success=False, error="timeout")
    except OSError as e:
        return PingResult(target=target, success=False, error=str(e))
    finally:
        sock.close()


def _ping_system(target: str, timeout: float = 2.0, count: int = 1) -> List[PingResult]:
    """Fallback using system ping command with safe parsing."""
    system = platform.system().lower()
    results: List[PingResult] = []

    if system == "windows":
        # ping -n count -w timeout_ms target
        timeout_ms = max(1, int(timeout * 1000))
        cmd = ["ping", "-n", str(count), "-w", str(timeout_ms), target]
    else:
        # Linux / macOS style
        # -c count -W timeout (seconds on most Linux)
        cmd = ["ping", "-c", str(count), "-W", str(max(1, int(timeout))), target]

    kwargs = {
        "capture_output": True,
        "text": True,
        "timeout": timeout * count + 5,
    }
    if system == "windows" and hasattr(subprocess, "CREATE_NO_WINDOW"):
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

    try:
        proc = subprocess.run(cmd, **kwargs)
        output = proc.stdout + proc.stderr
    except subprocess.TimeoutExpired:
        return [PingResult(target=target, success=False, error="timeout") for _ in range(count)]
    except FileNotFoundError:
        return [PingResult(target=target, success=False, error="ping_not_found")]
    except OSError as e:
        return [PingResult(target=target, success=False, error=str(e))]

    # Parse latencies
    # Windows: time=12ms or time<1ms
    # Linux: time=12.3 ms
    pattern = re.compile(r"time[=<]([\d.]+)\s*ms", re.IGNORECASE)
    matches = pattern.findall(output)

    if not matches and ("Destination host unreachable" in output or "timed out" in output.lower()
                        or "100% packet loss" in output.lower() or proc.returncode != 0):
        for _ in range(count):
            results.append(PingResult(target=target, success=False, error="unreachable_or_timeout"))
        return results

    for m in matches:
        try:
            lat = float(m)
            results.append(PingResult(target=target, success=True, latency_ms=round(lat, 2)))
        except ValueError:
            results.append(PingResult(target=target, success=False, error="parse_error"))

    # Fill missing if count > found
    while len(results) < count:
        results.append(PingResult(target=target, success=False, error="no_reply"))

    return results[:count]


def ping_once(target: str, timeout: float = 2.0) -> PingResult:
    """
    Perform a single ping.
    Tries raw socket first; falls back to system ping.
    """
    result = ping_once_raw(target, timeout=timeout)
    if result.error == "raw_socket_denied":
        series = _ping_system(target, timeout=timeout, count=1)
        return series[0] if series else PingResult(target=target, success=False, error="failed")
    return result


def ping_series(
    target: str,
    count: int = 4,
    timeout: float = 2.0,
    interval: float = 0.2,
) -> List[PingResult]:
    """Send a series of pings and return individual results."""
    results: List[PingResult] = []
    # Prefer system ping for series (more reliable across platforms without admin)
    system_results = _ping_system(target, timeout=timeout, count=count)
    if system_results and not all(r.error == "ping_not_found" for r in system_results):
        return system_results

    # Fallback to sequential raw/system once
    for i in range(count):
        r = ping_once(target, timeout=timeout)
        results.append(r)
        if i < count - 1:
            time.sleep(interval)
    return results


def calculate_jitter(latencies: Sequence[float]) -> float:
    """
    Calculate jitter as the average absolute difference between consecutive latencies.
    Returns 0.0 if fewer than 2 samples.
    """
    if len(latencies) < 2:
        return 0.0
    diffs = [abs(latencies[i] - latencies[i - 1]) for i in range(1, len(latencies))]
    return round(sum(diffs) / len(diffs), 2)


def calculate_packet_loss(results: Sequence[PingResult]) -> float:
    """Return packet loss percentage (0-100)."""
    if not results:
        return 0.0
    failed = sum(1 for r in results if not r.ok)
    return round((failed / len(results)) * 100.0, 1)


def summarize_ping(results: Sequence[PingResult]) -> dict:
    """Compute common statistics from a list of PingResult."""
    ok_latencies = [r.latency_ms for r in results if r.ok and r.latency_ms is not None]
    loss = calculate_packet_loss(results)
    jitter = calculate_jitter(ok_latencies)
    return {
        "count": len(results),
        "success_count": len(ok_latencies),
        "packet_loss_pct": loss,
        "min_ms": min(ok_latencies) if ok_latencies else None,
        "max_ms": max(ok_latencies) if ok_latencies else None,
        "avg_ms": round(sum(ok_latencies) / len(ok_latencies), 2) if ok_latencies else None,
        "jitter_ms": jitter,
        "latencies": ok_latencies,
    }
