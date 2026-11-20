"""Application settings."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox,
    QPushButton, QFormLayout, QFrame, QCheckBox, QMessageBox, QDoubleSpinBox
)

from app.core.config import get_config
from app.database.db import get_db


class SettingsPage(QWidget):
    settings_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._load()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(14)

        title = QLabel("Configurações")
        title.setObjectName("sectionTitle")
        root.addWidget(title)

        card = QFrame()
        card.setObjectName("card")
        form = QFormLayout(card)
        form.setContentsMargins(16, 14, 16, 14)
        form.setSpacing(10)

        self.target_edit = QLineEdit()
        form.addRow("Endereço padrão para testes:", self.target_edit)

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(200, 60000)
        self.interval_spin.setSuffix(" ms")
        form.addRow("Intervalo de monitoramento:", self.interval_spin)

        self.timeout_spin = QDoubleSpinBox()
        self.timeout_spin.setRange(0.5, 30.0)
        self.timeout_spin.setSingleStep(0.5)
        self.timeout_spin.setSuffix(" s")
        form.addRow("Timeout de ping:", self.timeout_spin)

        self.notify_check = QCheckBox("Ativar notificações")
        form.addRow(self.notify_check)

        self.latency_threshold = QDoubleSpinBox()
        self.latency_threshold.setRange(10, 1000)
        self.latency_threshold.setSuffix(" ms")
        form.addRow("Limite de latência alta:", self.latency_threshold)

        self.loss_threshold = QDoubleSpinBox()
        self.loss_threshold.setRange(0, 100)
        self.loss_threshold.setSuffix(" %")
        form.addRow("Limite de perda de pacotes:", self.loss_threshold)

        self.retention_spin = QSpinBox()
        self.retention_spin.setRange(1, 365)
        self.retention_spin.setSuffix(" dias")
        form.addRow("Retenção do histórico:", self.retention_spin)

        root.addWidget(card)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("Salvar configurações")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)

        clear_btn = QPushButton("Limpar histórico")
        clear_btn.setObjectName("dangerBtn")
        clear_btn.clicked.connect(self._clear_history)
        btn_row.addWidget(clear_btn)

        reset_btn = QPushButton("Restaurar padrões")
        reset_btn.clicked.connect(self._reset)
        btn_row.addWidget(reset_btn)
        btn_row.addStretch()
        root.addLayout(btn_row)

        root.addStretch()

        note = QLabel("Tema: escuro (fixo)  •  Idioma: Português (Brasil)")
        note.setObjectName("muted")
        root.addWidget(note)

    def _load(self) -> None:
        cfg = get_config()
        self.target_edit.setText(cfg.ping_target)
        self.interval_spin.setValue(cfg.update_interval_ms)
        self.timeout_spin.setValue(float(cfg.get("timeout_sec", 2.0)))
        self.notify_check.setChecked(bool(cfg.get("notifications_enabled", True)))
        self.latency_threshold.setValue(float(cfg.get("latency_threshold_ms", 100)))
        self.loss_threshold.setValue(float(cfg.get("packet_loss_threshold_pct", 5)))
        self.retention_spin.setValue(int(cfg.get("history_retention_days", 30)))

    def _save(self) -> None:
        cfg = get_config()
        cfg.ping_target = self.target_edit.text().strip() or "8.8.8.8"
        cfg.update_interval_ms = self.interval_spin.value()
        cfg.set("timeout_sec", self.timeout_spin.value())
        cfg.set("notifications_enabled", self.notify_check.isChecked())
        cfg.set("latency_threshold_ms", self.latency_threshold.value())
        cfg.set("packet_loss_threshold_pct", self.loss_threshold.value())
        cfg.set("history_retention_days", self.retention_spin.value())
        cfg.save()
        self.settings_changed.emit()
        QMessageBox.information(self, "Configurações", "Configurações salvas com sucesso.")

    def _clear_history(self) -> None:
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "Isso apagará todo o histórico de medições. Continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            get_db().clear_all()
            QMessageBox.information(self, "Histórico", "Histórico limpo.")

    def _reset(self) -> None:
        get_config().reset_to_defaults()
        self._load()
        self.settings_changed.emit()
        QMessageBox.information(self, "Configurações", "Padrões restaurados.")
