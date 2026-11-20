"""Network interface information using psutil."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import psutil


def get_network_adapters() -> List[Dict[str, Any]]:
    """
    Return list of network interfaces with addresses and stats.
    """
    adapters: List[Dict[str, Any]] = []
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    io = psutil.net_io_counters(pernic=True)

    for name, addr_list in addrs.items():
        entry: Dict[str, Any] = {
            "name": name,
            "addresses": [],
            "is_up": False,
            "speed_mbps": None,
            "mtu": None,
            "bytes_sent": 0,
            "bytes_recv": 0,
        }
        for a in addr_list:
            addr_info = {
                "family": str(a.family),
                "address": a.address,
                "netmask": a.netmask,
                "broadcast": a.broadcast,
            }
            entry["addresses"].append(addr_info)

        if name in stats:
            s = stats[name]
            entry["is_up"] = s.isup
            entry["speed_mbps"] = s.speed if s.speed > 0 else None
            entry["mtu"] = s.mtu

        if name in io:
            counters = io[name]
            entry["bytes_sent"] = counters.bytes_sent
            entry["bytes_recv"] = counters.bytes_recv

        adapters.append(entry)

    return adapters


def get_default_gateway() -> Optional[str]:
    """Best-effort default gateway detection (IPv4)."""
    try:
        # psutil does not expose gateway directly on all platforms.
        # Use a simple approach via routing table on Linux, or netifaces-like fallback.
        import platform
        import subprocess
        import re

        system = platform.system().lower()
        if system == "linux":
            try:
                with open("/proc/net/route", "r") as f:
                    for line in f.readlines()[1:]:
                        parts = line.strip().split()
                        if len(parts) >= 3 and parts[1] == "00000000":
                            # Gateway is little-endian hex
                            gw_hex = parts[2]
                            gw = socket_inet_ntoa(int(gw_hex, 16))
                            return gw
            except OSError:
                pass
        elif system == "windows":
            try:
                kwargs = {
                    "capture_output": True,
                    "text": True,
                    "timeout": 5,
                }
                if hasattr(subprocess, "CREATE_NO_WINDOW"):
                    kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
                proc = subprocess.run(["route", "print", "0.0.0.0"], **kwargs)
                for line in proc.stdout.splitlines():
                    if "0.0.0.0" in line:
                        parts = line.split()
                        if len(parts) >= 3 and parts[0] == "0.0.0.0":
                            return parts[2]
            except (OSError, subprocess.TimeoutExpired):
                pass
    except Exception:
        pass
    return None


def socket_inet_ntoa(n: int) -> str:
    """Convert little-endian int to IPv4 string."""
    import struct
    import socket
    return socket.inet_ntoa(struct.pack("<I", n))


def get_io_counters() -> Dict[str, Any]:
    """Global network I/O counters."""
    c = psutil.net_io_counters()
    return {
        "bytes_sent": c.bytes_sent,
        "bytes_recv": c.bytes_recv,
        "packets_sent": c.packets_sent,
        "packets_recv": c.packets_recv,
        "errin": c.errin,
        "errout": c.errout,
        "dropin": c.dropin,
        "dropout": c.dropout,
    }
