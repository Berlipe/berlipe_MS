"""Continuous monitoring controls and history preview."""

from __future__ import annotations

from PySide6.QtCore import Signal, Slot, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QFormLayout
)

from app.core.config import get_config
from app.utils.formatters import format_ms, format_percent, format_timestamp
from app.core.constants import COLOR_SUCCESS, COLOR_DANGER


class MonitoringPage(QWidget):
    start_requested = Signal(str, int)   # target, interval_ms
    stop_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._load_defaults()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(14)

        title = QLabel("Monitoramento")
        title.setObjectName("sectionTitle")
        root.addWidget(title)

        # Controls card
        controls = QFrame()
        controls.setObjectName("card")
        form = QFormLayout(controls)
        form.setContentsMargins(16, 14, 16, 14)
        form.setSpacing(10)

        self.target_edit = QLineEdit()
        self.target_edit.setPlaceholderText("8.8.8.8 ou host.exemplo.com")
        form.addRow("Destino (IP ou host):", self.target_edit)

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(200, 60000)
        self.interval_spin.setSingleStep(100)
        self.interval_spin.setSuffix(" ms")
        form.addRow("Intervalo de atualização:", self.interval_spin)

        btn_row = QHBoxLayout()
        self.start_btn = QPushButton("Iniciar monitoramento")
        self.start_btn.setObjectName("primaryBtn")
        self.start_btn.clicked.connect(self._on_start)
        self.stop_btn = QPushButton("Parar")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop)
        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.stop_btn)
        btn_row.addStretch()
        form.addRow(btn_row)

        self.running_label = QLabel("Status: parado")
        form.addRow(self.running_label)

        root.addWidget(controls)

        # Recent samples table
        table_label = QLabel("Últimas medições")
        table_label.setObjectName("cardTitle")
        root.addWidget(table_label)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Horário", "Destino", "Latência", "Jitter", "Perda"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        root.addWidget(self.table, stretch=1)

    def _load_defaults(self) -> None:
        cfg = get_config()
        self.target_edit.setText(cfg.ping_target)
        self.interval_spin.setValue(cfg.update_interval_ms)

    def _on_start(self) -> None:
        target = self.target_edit.text().strip()
        if not target:
            return
        interval = self.interval_spin.value()
        cfg = get_config()
        cfg.ping_target = target
        cfg.update_interval_ms = interval
        cfg.save()
        self.start_requested.emit(target, interval)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.running_label.setText("Status: monitorando…")
        self.running_label.setStyleSheet(f"color: {COLOR_SUCCESS};")

    def _on_stop(self) -> None:
        self.stop_requested.emit()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.running_label.setText("Status: parado")
        self.running_label.setStyleSheet("")

    @Slot(dict)
    def on_result(self, data: dict) -> None:
        row = self.table.rowCount()
        self.table.insertRow(0)  # newest on top
        # Keep table reasonable
        if self.table.rowCount() > 200:
            self.table.setRowCount(200)

        ts = format_timestamp(data.get("timestamp", 0))
        target = data.get("target", "—")
        lat = format_ms(data.get("latency_ms"))
        jit = format_ms(data.get("jitter_ms"))
        loss = format_percent(data.get("packet_loss_pct"))

        self.table.setItem(0, 0, QTableWidgetItem(ts))
        self.table.setItem(0, 1, QTableWidgetItem(target))
        self.table.setItem(0, 2, QTableWidgetItem(lat))
        self.table.setItem(0, 3, QTableWidgetItem(jit))
        self.table.setItem(0, 4, QTableWidgetItem(loss))

    def set_stopped(self) -> None:
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.running_label.setText("Status: parado")
        self.running_label.setStyleSheet("")
