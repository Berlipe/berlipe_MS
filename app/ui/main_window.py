"""Main application window."""

from __future__ import annotations

from PySide6.QtCore import Qt, Slot, QSize
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QStackedWidget, QLabel, QStatusBar, QMessageBox, QApplication
)

from app.core.constants import APP_DISPLAY_NAME, APP_VERSION, SIDEBAR_WIDTH
from app.core.config import get_config
from app.ui.styles.theme import DARK_STYLESHEET
from app.ui.pages import (
    DashboardPage, MonitoringPage, ToolsPage, HistoryPage, SettingsPage
)
from app.workers.monitor_worker import MonitorWorker
from app.workers.tool_workers import (
    PingWorker, SpeedTestWorker, TracerouteWorker, PortCheckWorker, DnsWorker
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_DISPLAY_NAME}  v{APP_VERSION}")
        self.resize(1180, 720)
        self.setMinimumSize(900, 560)

        self.setStyleSheet(DARK_STYLESHEET)

        self._workers: list = []  # keep references

        self._build_ui()
        self._connect_signals()
        self._setup_monitor()

        self.statusBar().showMessage("Pronto")

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(SIDEBAR_WIDTH)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(10, 10, 10, 10)
        side_layout.setSpacing(4)

        title = QLabel("berlip_MS")
        title.setObjectName("sidebarTitle")
        side_layout.addWidget(title)
        sub = QLabel("Monitor de Rede")
        sub.setObjectName("sidebarSubtitle")
        side_layout.addWidget(sub)

        self.nav_buttons: list[QPushButton] = []
        nav_items = [
            ("Dashboard", 0),
            ("Monitoramento", 1),
            ("Ferramentas", 2),
            ("Histórico", 3),
            ("Configurações", 4),
        ]
        for text, idx in nav_items:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, i=idx: self._navigate(i))
            side_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        side_layout.addStretch()
        version = QLabel(f"v{APP_VERSION}")
        version.setObjectName("muted")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        side_layout.addWidget(version)

        layout.addWidget(sidebar)

        # Pages
        self.stack = QStackedWidget()
        self.page_dashboard = DashboardPage()
        self.page_monitoring = MonitoringPage()
        self.page_tools = ToolsPage()
        self.page_history = HistoryPage()
        self.page_settings = SettingsPage()

        self.stack.addWidget(self.page_dashboard)
        self.stack.addWidget(self.page_monitoring)
        self.stack.addWidget(self.page_tools)
        self.stack.addWidget(self.page_history)
        self.stack.addWidget(self.page_settings)

        layout.addWidget(self.stack, stretch=1)

        self.nav_buttons[0].setChecked(True)

    def _navigate(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        if index == 3:  # history
            self.page_history.refresh()

    def _setup_monitor(self) -> None:
        self.monitor = MonitorWorker()
        self.monitor.result_ready.connect(self.page_dashboard.on_monitor_result)
        self.monitor.result_ready.connect(self.page_monitoring.on_result)
        self.monitor.status_changed.connect(self._on_monitor_status)
        self.monitor.error_occurred.connect(self._on_worker_error)

    def _connect_signals(self) -> None:
        self.page_monitoring.start_requested.connect(self._start_monitoring)
        self.page_monitoring.stop_requested.connect(self._stop_monitoring)

        self.page_tools.request_ping.connect(self._run_ping)
        self.page_tools.request_speed.connect(self._run_speed)
        self.page_tools.request_traceroute.connect(self._run_traceroute)
        self.page_tools.request_port.connect(self._run_port)
        self.page_tools.request_dns.connect(self._run_dns)

        self.page_settings.settings_changed.connect(self._on_settings_changed)

    # ---- monitoring ----
    @Slot(str, int)
    def _start_monitoring(self, target: str, interval_ms: int) -> None:
        cfg = get_config()
        self.monitor.configure(target, interval_ms, float(cfg.get("timeout_sec", 2.0)))
        self.monitor.start_monitoring()
        self.statusBar().showMessage(f"Monitorando {target}…")

    @Slot()
    def _stop_monitoring(self) -> None:
        self.monitor.stop_monitoring()
        self.page_monitoring.set_stopped()
        self.statusBar().showMessage("Monitoramento parado")

    @Slot(str)
    def _on_monitor_status(self, status: str) -> None:
        if status == "stopped":
            self.page_monitoring.set_stopped()

    # ---- tools ----
    @Slot(str, int)
    def _run_ping(self, target: str, count: int) -> None:
        w = PingWorker(target, count=count)
        w.finished_ok.connect(self.page_tools.show_ping_result)
        w.failed.connect(self.page_tools.show_error)
        w.finished.connect(lambda: self._cleanup_worker(w))
        self._workers.append(w)
        w.start()
        self.statusBar().showMessage(f"Ping em {target}…")

    @Slot()
    def _run_speed(self) -> None:
        w = SpeedTestWorker()
        w.finished_ok.connect(self._on_speed_done)
        w.failed.connect(self.page_tools.show_error)
        w.progress.connect(lambda s: self.statusBar().showMessage(f"Teste de velocidade: {s}…"))
        w.finished.connect(lambda: self._cleanup_worker(w))
        self._workers.append(w)
        w.start()

    @Slot(dict)
    def _on_speed_done(self, data: dict) -> None:
        self.page_tools.show_speed_result(data)
        d = data.get("download", {}).get("mbps")
        u = data.get("upload", {}).get("mbps")
        self.page_dashboard.update_speed(d, u)
        self.statusBar().showMessage("Teste de velocidade concluído")

    @Slot(str)
    def _run_traceroute(self, target: str) -> None:
        w = TracerouteWorker(target)
        w.finished_ok.connect(self.page_tools.show_trace_result)
        w.failed.connect(self.page_tools.show_error)
        w.finished.connect(lambda: self._cleanup_worker(w))
        self._workers.append(w)
        w.start()
        self.statusBar().showMessage(f"Traceroute para {target}…")

    @Slot(str, int)
    def _run_port(self, host: str, port: int) -> None:
        w = PortCheckWorker(host, port)
        w.finished_ok.connect(self.page_tools.show_port_result)
        w.failed.connect(self.page_tools.show_error)
        w.finished.connect(lambda: self._cleanup_worker(w))
        self._workers.append(w)
        w.start()
        self.statusBar().showMessage(f"Verificando {host}:{port}…")

    @Slot(str, bool)
    def _run_dns(self, query: str, reverse: bool) -> None:
        w = DnsWorker(query, reverse=reverse)
        w.finished_ok.connect(self.page_tools.show_dns_result)
        w.failed.connect(self.page_tools.show_error)
        w.finished.connect(lambda: self._cleanup_worker(w))
        self._workers.append(w)
        w.start()
        self.statusBar().showMessage(f"DNS: {query}…")

    def _cleanup_worker(self, w) -> None:
        if w in self._workers:
            self._workers.remove(w)
        w.deleteLater()

    @Slot(str)
    def _on_worker_error(self, msg: str) -> None:
        self.statusBar().showMessage(f"Erro: {msg}")

    @Slot()
    def _on_settings_changed(self) -> None:
        self.statusBar().showMessage("Configurações atualizadas")

    def closeEvent(self, event) -> None:
        self.monitor.stop_monitoring()
        self.monitor.wait(2000)
        for w in list(self._workers):
            if w.isRunning():
                w.wait(1000)
        get_config().save()
        super().closeEvent(event)
