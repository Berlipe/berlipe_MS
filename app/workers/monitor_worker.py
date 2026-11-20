"""Background continuous monitoring worker."""

from __future__ import annotations

import time
from typing import Optional

from PySide6.QtCore import QThread, Signal, QMutex, QMutexLocker

from app.network.ping import ping_once, ping_series, calculate_jitter, calculate_packet_loss, summarize_ping
from app.database.db import get_db
from app.core.config import get_config


class MonitorWorker(QThread):
    """
    Continuously pings a target at configurable interval and emits results.
    Never blocks the GUI thread.
    """

    result_ready = Signal(dict)          # single sample result
    series_ready = Signal(dict)          # aggregated stats
    status_changed = Signal(str)         # "running" | "stopped" | "error"
    error_occurred = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._mutex = QMutex()
        self._running = False
        self._target = "8.8.8.8"
        self._interval_ms = 1000
        self._timeout = 2.0
        self._history_latencies: list[float] = []
        self._max_history = 60  # for jitter window

    def configure(self, target: str, interval_ms: int = 1000, timeout: float = 2.0) -> None:
        with QMutexLocker(self._mutex):
            self._target = target
            self._interval_ms = max(200, interval_ms)
            self._timeout = timeout

    def start_monitoring(self) -> None:
        with QMutexLocker(self._mutex):
            if self._running:
                return
            self._running = True
        if not self.isRunning():
            self.start()
        self.status_changed.emit("running")

    def stop_monitoring(self) -> None:
        with QMutexLocker(self._mutex):
            self._running = False
        self.status_changed.emit("stopped")

    def is_monitoring(self) -> bool:
        with QMutexLocker(self._mutex):
            return self._running

    def run(self) -> None:
        db = get_db()
        while True:
            with QMutexLocker(self._mutex):
                if not self._running:
                    break
                target = self._target
                interval = self._interval_ms / 1000.0
                timeout = self._timeout

            try:
                result = ping_once(target, timeout=timeout)
                latency = result.latency_ms if result.ok else None

                with QMutexLocker(self._mutex):
                    if latency is not None:
                        self._history_latencies.append(latency)
                        if len(self._history_latencies) > self._max_history:
                            self._history_latencies.pop(0)
                    hist = list(self._history_latencies)

                jitter = calculate_jitter(hist) if len(hist) >= 2 else 0.0
                # For continuous mode we treat single packet loss as 0 or 100
                loss = 0.0 if result.ok else 100.0

                payload = {
                    "timestamp": result.timestamp,
                    "target": target,
                    "success": result.ok,
                    "latency_ms": latency,
                    "jitter_ms": jitter,
                    "packet_loss_pct": loss,
                    "error": result.error,
                }
                self.result_ready.emit(payload)

                # Persist every successful sample (or failures too)
                try:
                    db.insert_measurement(
                        target=target,
                        latency_ms=latency,
                        jitter_ms=jitter,
                        packet_loss_pct=loss,
                        success=result.ok,
                    )
                except Exception:
                    pass  # non-fatal

            except Exception as e:
                self.error_occurred.emit(str(e))

            # Sleep in small slices so stop is responsive
            slept = 0.0
            while slept < interval:
                with QMutexLocker(self._mutex):
                    if not self._running:
                        return
                time.sleep(0.05)
                slept += 0.05

        self.status_changed.emit("stopped")
