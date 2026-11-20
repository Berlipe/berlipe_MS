"""DNS resolution helpers."""

from __future__ import annotations

import socket
from typing import List, Optional, Tuple


def resolve_hostname(hostname: str, family: int = socket.AF_UNSPEC) -> List[str]:
    """
    Resolve hostname to list of IP addresses.
    Returns empty list on failure.
    """
    try:
        infos = socket.getaddrinfo(hostname, None, family, socket.SOCK_STREAM)
        ips = []
        seen = set()
        for info in infos:
            ip = info[4][0]
            if ip not in seen:
                seen.add(ip)
                ips.append(ip)
        return ips
    except socket.gaierror:
        return []


def reverse_lookup(ip: str) -> Optional[str]:
    """Reverse DNS lookup. Returns hostname or None."""
    try:
        host, _, _ = socket.gethostbyaddr(ip)
        return host
    except (socket.herror, socket.gaierror, OSError):
        return None


def resolve_with_details(hostname: str) -> dict:
    """Return detailed resolution info."""
    result = {
        "hostname": hostname,
        "ipv4": [],
        "ipv6": [],
        "error": None,
    }
    try:
        infos = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
        for info in infos:
            family, _, _, _, sockaddr = info
            ip = sockaddr[0]
            if family == socket.AF_INET:
                if ip not in result["ipv4"]:
                    result["ipv4"].append(ip)
            elif family == socket.AF_INET6:
                if ip not in result["ipv6"]:
                    result["ipv6"].append(ip)
    except socket.gaierror as e:
        result["error"] = str(e)
    return result
