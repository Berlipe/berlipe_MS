"""Real-time latency chart using pyqtgraph."""

from __future__ import annotations

from collections import deque
from typing import Deque, Optional

import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout

from app.core.constants import COLOR_LATENCY, COLOR_BG, COLOR_SURFACE, COLOR_TEXT_DIM, MAX_HISTORY_POINTS_CHART


class LatencyChart(QWidget):
    def __init__(self, parent=None, max_points: int = MAX_HISTORY_POINTS_CHART):
        super().__init__(parent)
        self.max_points = max_points
        self._data: Deque[float] = deque(maxlen=max_points)
        self._times: Deque[float] = deque(maxlen=max_points)
        self._t0: Optional[float] = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        pg.setConfigOptions(antialias=True, background=COLOR_SURFACE, foreground=COLOR_TEXT_DIM)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground(COLOR_SURFACE)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.2)
        self.plot_widget.setLabel("left", "Latência", units="ms")
        self.plot_widget.setLabel("bottom", "Tempo", units="s")
        self.plot_widget.setMinimumHeight(180)
        self.plot_widget.getAxis("left").setPen(pg.mkPen(COLOR_TEXT_DIM))
        self.plot_widget.getAxis("bottom").setPen(pg.mkPen(COLOR_TEXT_DIM))

        self.curve = self.plot_widget.plot(
            pen=pg.mkPen(COLOR_LATENCY, width=2),
            fillLevel=0,
            brush=pg.mkBrush(59, 130, 246, 40),
        )
        layout.addWidget(self.plot_widget)

    def add_point(self, latency_ms: float, timestamp: Optional[float] = None) -> None:
        import time
        ts = timestamp if timestamp is not None else time.time()
        if self._t0 is None:
            self._t0 = ts
        self._times.append(ts - self._t0)
        self._data.append(latency_ms)
        self._redraw()

    def clear(self) -> None:
        self._data.clear()
        self._times.clear()
        self._t0 = None
        self.curve.setData([], [])

    def _redraw(self) -> None:
        if not self._data:
            return
        x = np.array(self._times)
        y = np.array(self._data)
        self.curve.setData(x, y)
