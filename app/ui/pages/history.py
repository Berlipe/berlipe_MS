"""History view and export."""

from __future__ import annotations

import time
from pathlib import Path

from PySide6.QtCore import Slot, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox, QComboBox, QSpinBox
)

from app.database.db import get_db
from app.utils.formatters import format_ms, format_percent, format_timestamp, format_mbps
from app.core.config import get_config


class HistoryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)

        title = QLabel("Histórico")
        title.setObjectName("sectionTitle")
        root.addWidget(title)

        # Filters
        filt = QHBoxLayout()
        filt.addWidget(QLabel("Período:"))
        self.period_combo = QComboBox()
        self.period_combo.addItems([
            "Últimas 24 horas",
            "Últimos 7 dias",
            "Últimos 30 dias",
            "Tudo",
        ])
        self.period_combo.currentIndexChanged.connect(self.refresh)
        filt.addWidget(self.period_combo)

        filt.addWidget(QLabel("Limite:"))
        self.limit_spin = QSpinBox()
        self.limit_spin.setRange(50, 5000)
        self.limit_spin.setValue(500)
        self.limit_spin.setSingleStep(50)
        filt.addWidget(self.limit_spin)

        refresh_btn = QPushButton("Atualizar")
        refresh_btn.clicked.connect(self.refresh)
        filt.addWidget(refresh_btn)
        filt.addStretch()

        export_csv = QPushButton("Exportar CSV")
        export_csv.clicked.connect(lambda: self._export("csv"))
        filt.addWidget(export_csv)

        export_json = QPushButton("Exportar JSON")
        export_json.clicked.connect(lambda: self._export("json"))
        filt.addWidget(export_json)

        root.addLayout(filt)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "Horário", "Destino", "Latência", "Jitter", "Perda %",
            "Download", "Upload", "OK"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        root.addWidget(self.table, stretch=1)

        self.count_label = QLabel("0 registros")
        root.addWidget(self.count_label)

        self.refresh()

    def _period_range(self) -> tuple[float | None, float | None]:
        now = time.time()
        idx = self.period_combo.currentIndex()
        if idx == 0:
            return now - 86400, now
        if idx == 1:
            return now - 7 * 86400, now
        if idx == 2:
            return now - 30 * 86400, now
        return None, None

    def refresh(self) -> None:
        db = get_db()
        start, end = self._period_range()
        rows = db.query_measurements(
            start_ts=start,
            end_ts=end,
            limit=self.limit_spin.value(),
        )
        self.table.setRowCount(0)
        for r in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(format_timestamp(r["timestamp"])))
            self.table.setItem(row, 1, QTableWidgetItem(r.get("target") or "—"))
            self.table.setItem(row, 2, QTableWidgetItem(format_ms(r.get("latency_ms"))))
            self.table.setItem(row, 3, QTableWidgetItem(format_ms(r.get("jitter_ms"))))
            self.table.setItem(row, 4, QTableWidgetItem(format_percent(r.get("packet_loss_pct"))))
            self.table.setItem(row, 5, QTableWidgetItem(format_mbps(r.get("download_mbps"))))
            self.table.setItem(row, 6, QTableWidgetItem(format_mbps(r.get("upload_mbps"))))
            self.table.setItem(row, 7, QTableWidgetItem("Sim" if r.get("success") else "Não"))
        total = db.count_measurements(start_ts=start, end_ts=end)
        self.count_label.setText(f"{len(rows)} exibidos de {total} no período")

    def _export(self, fmt: str) -> None:
        cfg = get_config()
        start_dir = cfg.get("last_export_dir") or str(Path.home())
        if fmt == "csv":
            path, _ = QFileDialog.getSaveFileName(
                self, "Exportar CSV", str(Path(start_dir) / "berlip_ms_history.csv"),
                "CSV (*.csv)"
            )
        else:
            path, _ = QFileDialog.getSaveFileName(
                self, "Exportar JSON", str(Path(start_dir) / "berlip_ms_history.json"),
                "JSON (*.json)"
            )
        if not path:
            return
        start, end = self._period_range()
        db = get_db()
        try:
            if fmt == "csv":
                n = db.export_csv(Path(path), start_ts=start, end_ts=end)
            else:
                n = db.export_json(Path(path), start_ts=start, end_ts=end)
            cfg.set("last_export_dir", str(Path(path).parent))
            cfg.save()
            QMessageBox.information(self, "Exportação", f"{n} registros exportados para:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))
