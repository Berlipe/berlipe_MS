"""Simple traceroute using system command (cross-platform safe parsing)."""

from __future__ import annotations

import platform
import re
import subprocess
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Hop:
    hop: int
    ip: Optional[str]
    hostname: Optional[str]
    latency_ms: Optional[float]
    error: Optional[str] = None


def traceroute(
    target: str,
    max_hops: int = 30,
    timeout_per_hop: float = 2.0,
) -> List[Hop]:
    """
    Perform traceroute using system tools.
    Returns list of Hop objects.
    """
    system = platform.system().lower()
    hops: List[Hop] = []

    if system == "windows":
        cmd = ["tracert", "-d", "-h", str(max_hops), "-w", str(int(timeout_per_hop * 1000)), target]
    else:
        # Linux traceroute or traceroute.db
        cmd = ["traceroute", "-n", "-m", str(max_hops), "-w", str(int(timeout_per_hop)), target]

    kwargs = {
        "capture_output": True,
        "text": True,
        "timeout": max_hops * timeout_per_hop + 10,
    }
    if system == "windows" and hasattr(subprocess, "CREATE_NO_WINDOW"):
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    try:
        proc = subprocess.run(cmd, **kwargs)
        output = proc.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
        return [Hop(hop=0, ip=None, hostname=None, latency_ms=None, error=str(e))]

    if system == "windows":
        # Example:  1    <1 ms    <1 ms    <1 ms  192.168.1.1
        # or        2     *        *        *     Request timed out.
        line_re = re.compile(
            r"^\s*(\d+)\s+(?:<\d+|\d+)\s*ms\s+(?:<\d+|\d+)\s*ms\s+(?:<\d+|\d+)\s*ms\s+(\S+)",
            re.IGNORECASE,
        )
        timeout_re = re.compile(r"^\s*(\d+)\s+\*\s+\*\s+\*")
        for line in output.splitlines():
            m = line_re.search(line)
            if m:
                hop_num = int(m.group(1))
                ip = m.group(2)
                # Extract first latency
                lat_match = re.search(r"(<\d+|\d+)\s*ms", line)
                lat = None
                if lat_match:
                    val = lat_match.group(1).replace("<", "")
                    try:
                        lat = float(val)
                    except ValueError:
                        pass
                hops.append(Hop(hop=hop_num, ip=ip, hostname=None, latency_ms=lat))
            else:
                m2 = timeout_re.search(line)
                if m2:
                    hops.append(Hop(hop=int(m2.group(1)), ip=None, hostname=None, latency_ms=None, error="timeout"))
    else:
        # Linux:  1  192.168.1.1  0.512 ms  0.401 ms  0.389 ms
        # or      2  * * *
        line_re = re.compile(r"^\s*(\d+)\s+(\S+)\s+([\d.]+)\s*ms")
        timeout_re = re.compile(r"^\s*(\d+)\s+\*\s+\*\s+\*")
        for line in output.splitlines():
            m = line_re.search(line)
            if m:
                hops.append(
                    Hop(
                        hop=int(m.group(1)),
                        ip=m.group(2) if m.group(2) != "*" else None,
                        hostname=None,
                        latency_ms=float(m.group(3)),
                    )
                )
            else:
                m2 = timeout_re.search(line)
                if m2:
                    hops.append(Hop(hop=int(m2.group(1)), ip=None, hostname=None, latency_ms=None, error="timeout"))

    return hops
