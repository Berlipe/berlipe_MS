"""Simple dual-line speed chart (download / upload)."""

from __future__ import annotations

from collections import deque
from typing import Deque, Optional

import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout

from app.core.constants import (
    COLOR_DOWNLOAD,
    COLOR_UPLOAD,
    COLOR_SURFACE,
    COLOR_TEXT_DIM,
    MAX_HISTORY_POINTS_CHART,
)


class SpeedChart(QWidget):
    def __init__(self, parent=None, max_points: int = 60):
        super().__init__(parent)
        self.max_points = max_points
        self._down: Deque[float] = deque(maxlen=max_points)
        self._up: Deque[float] = deque(maxlen=max_points)
        self._times: Deque[float] = deque(maxlen=max_points)
        self._t0: Optional[float] = None
        self._counter = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground(COLOR_SURFACE)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.2)
        self.plot_widget.setLabel("left", "Velocidade", units="Mbps")
        self.plot_widget.setLabel("bottom", "Amostra")
        self.plot_widget.setMinimumHeight(160)
        self.plot_widget.addLegend(offset=(10, 10))

        self.down_curve = self.plot_widget.plot(
            pen=pg.mkPen(COLOR_DOWNLOAD, width=2),
            name="Download",
        )
        self.up_curve = self.plot_widget.plot(
            pen=pg.mkPen(COLOR_UPLOAD, width=2),
            name="Upload",
        )
        layout.addWidget(self.plot_widget)

    def add_point(self, download_mbps: Optional[float], upload_mbps: Optional[float]) -> None:
        self._counter += 1
        self._times.append(float(self._counter))
        self._down.append(download_mbps if download_mbps is not None else 0.0)
        self._up.append(upload_mbps if upload_mbps is not None else 0.0)
        self._redraw()

    def clear(self) -> None:
        self._down.clear()
        self._up.clear()
        self._times.clear()
        self._counter = 0
        self.down_curve.setData([], [])
        self.up_curve.setData([], [])

    def _redraw(self) -> None:
        x = np.array(self._times)
        self.down_curve.setData(x, np.array(self._down))
        self.up_curve.setData(x, np.array(self._up))
