"""TCP port connectivity check."""

from __future__ import annotations

import socket
from dataclasses import dataclass
from typing import Optional


@dataclass
class PortCheckResult:
    host: str
    port: int
    open: bool
    latency_ms: Optional[float] = None
    error: Optional[str] = None


def check_tcp_port(
    host: str,
    port: int,
    timeout: float = 3.0,
) -> PortCheckResult:
    """
    Attempt TCP connection to host:port.
    Returns whether the port appears open and approximate latency.
    """
    import time

    if not (1 <= port <= 65535):
        return PortCheckResult(host=host, port=port, open=False, error="invalid_port")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    start = time.perf_counter()
    try:
        sock.connect((host, port))
        latency = (time.perf_counter() - start) * 1000.0
        return PortCheckResult(
            host=host,
            port=port,
            open=True,
            latency_ms=round(latency, 2),
        )
    except socket.timeout:
        return PortCheckResult(host=host, port=port, open=False, error="timeout")
    except ConnectionRefusedError:
        return PortCheckResult(host=host, port=port, open=False, error="connection_refused")
    except OSError as e:
        return PortCheckResult(host=host, port=port, open=False, error=str(e))
    finally:
        sock.close()
