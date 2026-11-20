"""Reusable metric display card."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout


class MetricCard(QFrame):
    def __init__(
        self,
        title: str,
        value: str = "—",
        unit: str = "",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumHeight(90)
        self.setMaximumHeight(110)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("cardTitle")
        layout.addWidget(self.title_label)

        value_row = QHBoxLayout()
        value_row.setSpacing(6)

        self.value_label = QLabel(value)
        self.value_label.setObjectName("cardValue")
        value_row.addWidget(self.value_label)

        self.unit_label = QLabel(unit)
        self.unit_label.setObjectName("cardUnit")
        self.unit_label.setAlignment(Qt.AlignmentFlag.AlignBottom)
        value_row.addWidget(self.unit_label)
        value_row.addStretch()

        layout.addLayout(value_row)
        layout.addStretch()

    def set_value(self, value: str, unit: str | None = None) -> None:
        self.value_label.setText(value)
        if unit is not None:
            self.unit_label.setText(unit)

    def set_color(self, color: str) -> None:
        self.value_label.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: 700;")
