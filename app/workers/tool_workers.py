"""One-shot workers for tools page."""

from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import QThread, Signal

from app.network.ping import ping_series, summarize_ping, PingResult
from app.network.speed import estimate_download_speed, estimate_upload_speed
from app.network.traceroute import traceroute, Hop
from app.network.port_scan import check_tcp_port, PortCheckResult
from app.network.dns_tools import resolve_with_details, reverse_lookup


class PingWorker(QThread):
    finished_ok = Signal(dict)
    failed = Signal(str)

    def __init__(self, target: str, count: int = 4, timeout: float = 2.0, parent=None):
        super().__init__(parent)
        self.target = target
        self.count = count
        self.timeout = timeout

    def run(self) -> None:
        try:
            results: List[PingResult] = ping_series(self.target, count=self.count, timeout=self.timeout)
            summary = summarize_ping(results)
            summary["target"] = self.target
            summary["raw"] = [
                {
                    "success": r.ok,
                    "latency_ms": r.latency_ms,
                    "error": r.error,
                }
                for r in results
            ]
            self.finished_ok.emit(summary)
        except Exception as e:
            self.failed.emit(str(e))


class SpeedTestWorker(QThread):
    progress = Signal(str)
    finished_ok = Signal(dict)
    failed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self) -> None:
        try:
            self.progress.emit("download")
            down = estimate_download_speed()
            self.progress.emit("upload")
            up = estimate_upload_speed()
            payload = {
                "download": {
                    "success": down.success,
                    "mbps": down.mbps,
                    "error": down.error,
                    "bytes": down.bytes_transferred,
                    "duration": down.duration_sec,
                },
                "upload": {
                    "success": up.success,
                    "mbps": up.mbps,
                    "error": up.error,
                    "bytes": up.bytes_transferred,
                    "duration": up.duration_sec,
                },
            }
            self.finished_ok.emit(payload)
        except Exception as e:
            self.failed.emit(str(e))


class TracerouteWorker(QThread):
    finished_ok = Signal(list)
    failed = Signal(str)

    def __init__(self, target: str, max_hops: int = 20, parent=None):
        super().__init__(parent)
        self.target = target
        self.max_hops = max_hops

    def run(self) -> None:
        try:
            hops = traceroute(self.target, max_hops=self.max_hops)
            payload = [
                {
                    "hop": h.hop,
                    "ip": h.ip,
                    "hostname": h.hostname,
                    "latency_ms": h.latency_ms,
                    "error": h.error,
                }
                for h in hops
            ]
            self.finished_ok.emit(payload)
        except Exception as e:
            self.failed.emit(str(e))


class PortCheckWorker(QThread):
    finished_ok = Signal(dict)
    failed = Signal(str)

    def __init__(self, host: str, port: int, timeout: float = 3.0, parent=None):
        super().__init__(parent)
        self.host = host
        self.port = port
        self.timeout = timeout

    def run(self) -> None:
        try:
            r: PortCheckResult = check_tcp_port(self.host, self.port, timeout=self.timeout)
            self.finished_ok.emit({
                "host": r.host,
                "port": r.port,
                "open": r.open,
                "latency_ms": r.latency_ms,
                "error": r.error,
            })
        except Exception as e:
            self.failed.emit(str(e))


class DnsWorker(QThread):
    finished_ok = Signal(dict)
    failed = Signal(str)

    def __init__(self, query: str, reverse: bool = False, parent=None):
        super().__init__(parent)
        self.query = query
        self.reverse = reverse

    def run(self) -> None:
        try:
            if self.reverse:
                host = reverse_lookup(self.query)
                self.finished_ok.emit({
                    "query": self.query,
                    "reverse": True,
                    "hostname": host,
                })
            else:
                details = resolve_with_details(self.query)
                self.finished_ok.emit(details)
        except Exception as e:
            self.failed.emit(str(e))
