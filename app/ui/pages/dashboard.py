"""Dashboard page – live overview."""

from __future__ import annotations

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QFrame, QPushButton
)

from app.ui.widgets.metric_card import MetricCard
from app.ui.widgets.latency_chart import LatencyChart
from app.ui.widgets.speed_chart import SpeedChart
from app.core.constants import COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING, COLOR_TEXT_DIM
from app.utils.formatters import format_ms, format_mbps, format_percent


class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title = QLabel("Dashboard")
        title.setObjectName("sectionTitle")
        header.addWidget(title)
        header.addStretch()

        self.status_label = QLabel("● Offline")
        self.status_label.setStyleSheet(f"color: {COLOR_TEXT_DIM}; font-weight: 600;")
        header.addWidget(self.status_label)
        root.addLayout(header)

        # Metric cards
        cards_layout = QGridLayout()
        cards_layout.setSpacing(12)

        self.card_ping = MetricCard("Ping atual", "—", "ms")
        self.card_avg = MetricCard("Ping médio", "—", "ms")
        self.card_jitter = MetricCard("Jitter", "—", "ms")
        self.card_loss = MetricCard("Perda de pacotes", "—", "%")
        self.card_down = MetricCard("Download", "—", "Mbps")
        self.card_up = MetricCard("Upload", "—", "Mbps")

        cards_layout.addWidget(self.card_ping, 0, 0)
        cards_layout.addWidget(self.card_avg, 0, 1)
        cards_layout.addWidget(self.card_jitter, 0, 2)
        cards_layout.addWidget(self.card_loss, 1, 0)
        cards_layout.addWidget(self.card_down, 1, 1)
        cards_layout.addWidget(self.card_up, 1, 2)

        root.addLayout(cards_layout)

        # Charts
        charts_row = QHBoxLayout()
        charts_row.setSpacing(12)

        lat_frame = QFrame()
        lat_frame.setObjectName("card")
        lat_layout = QVBoxLayout(lat_frame)
        lat_layout.setContentsMargins(12, 10, 12, 10)
        lat_title = QLabel("Latência em tempo real")
        lat_title.setObjectName("cardTitle")
        lat_layout.addWidget(lat_title)
        self.latency_chart = LatencyChart()
        lat_layout.addWidget(self.latency_chart)
        charts_row.addWidget(lat_frame, stretch=2)

        spd_frame = QFrame()
        spd_frame.setObjectName("card")
        spd_layout = QVBoxLayout(spd_frame)
        spd_layout.setContentsMargins(12, 10, 12, 10)
        spd_title = QLabel("Velocidade")
        spd_title.setObjectName("cardTitle")
        spd_layout.addWidget(spd_title)
        self.speed_chart = SpeedChart()
        spd_layout.addWidget(self.speed_chart)
        charts_row.addWidget(spd_frame, stretch=1)

        root.addLayout(charts_row, stretch=1)

        # Running averages for cards
        self._latencies: list[float] = []
        self._max_avg_window = 30

    @Slot(dict)
    def on_monitor_result(self, data: dict) -> None:
        success = data.get("success", False)
        latency = data.get("latency_ms")
        jitter = data.get("jitter_ms")
        loss = data.get("packet_loss_pct")

        if success and latency is not None:
            self.card_ping.set_value(f"{latency:.1f}")
            self.card_ping.set_color(COLOR_SUCCESS if latency < 80 else (COLOR_WARNING if latency < 150 else COLOR_DANGER))
            self._latencies.append(latency)
            if len(self._latencies) > self._max_avg_window:
                self._latencies.pop(0)
            avg = sum(self._latencies) / len(self._latencies)
            self.card_avg.set_value(f"{avg:.1f}")
            self.latency_chart.add_point(latency, data.get("timestamp"))
            self.status_label.setText("● Online")
            self.status_label.setStyleSheet(f"color: {COLOR_SUCCESS}; font-weight: 600;")
        else:
            self.card_ping.set_value("—")
            self.card_ping.set_color(COLOR_DANGER)
            self.status_label.setText("● Offline / Erro")
            self.status_label.setStyleSheet(f"color: {COLOR_DANGER}; font-weight: 600;")

        if jitter is not None:
            self.card_jitter.set_value(f"{jitter:.1f}")
        if loss is not None:
            self.card_loss.set_value(f"{loss:.1f}")
            self.card_loss.set_color(COLOR_SUCCESS if loss < 1 else (COLOR_WARNING if loss < 5 else COLOR_DANGER))

    def update_speed(self, download: float | None, upload: float | None) -> None:
        if download is not None:
            self.card_down.set_value(f"{download:.2f}")
        if upload is not None:
            self.card_up.set_value(f"{upload:.2f}")
        self.speed_chart.add_point(download, upload)

    def set_status(self, online: bool, text: str | None = None) -> None:
        if online:
            self.status_label.setText(text or "● Online")
            self.status_label.setStyleSheet(f"color: {COLOR_SUCCESS}; font-weight: 600;")
        else:
            self.status_label.setText(text or "● Offline")
            self.status_label.setStyleSheet(f"color: {COLOR_TEXT_DIM}; font-weight: 600;")
