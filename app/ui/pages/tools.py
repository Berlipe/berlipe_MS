"""Network tools page."""

from __future__ import annotations

from PySide6.QtCore import Signal, Slot, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox,
    QPushButton, QTextEdit, QTabWidget, QFormLayout, QFrame, QComboBox
)

from app.core.config import get_config


class ToolsPage(QWidget):
    # Signals to request work from main window / workers
    request_ping = Signal(str, int)
    request_speed = Signal()
    request_traceroute = Signal(str)
    request_port = Signal(str, int)
    request_dns = Signal(str, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)

        title = QLabel("Ferramentas")
        title.setObjectName("sectionTitle")
        root.addWidget(title)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_ping_tab(), "Ping / Jitter / Perda")
        self.tabs.addTab(self._build_speed_tab(), "Velocidade")
        self.tabs.addTab(self._build_dns_tab(), "DNS")
        self.tabs.addTab(self._build_trace_tab(), "Traceroute")
        self.tabs.addTab(self._build_port_tab(), "Portas TCP")
        self.tabs.addTab(self._build_adapters_tab(), "Adaptadores")
        root.addWidget(self.tabs)

    def _build_ping_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        form = QFormLayout()
        self.ping_target = QLineEdit(get_config().ping_target)
        self.ping_count = QSpinBox()
        self.ping_count.setRange(1, 50)
        self.ping_count.setValue(4)
        form.addRow("Destino:", self.ping_target)
        form.addRow("Quantidade:", self.ping_count)
        layout.addLayout(form)

        btn = QPushButton("Executar teste de ping")
        btn.setObjectName("primaryBtn")
        btn.clicked.connect(self._do_ping)
        layout.addWidget(btn)

        self.ping_output = QTextEdit()
        self.ping_output.setReadOnly(True)
        self.ping_output.setPlaceholderText("Resultados do ping aparecerão aqui…")
        layout.addWidget(self.ping_output)
        return w

    def _build_speed_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        info = QLabel(
            "Teste aproximado de velocidade usando endpoints públicos (Cloudflare/OVH).\n"
            "Não substitui um speedtest completo, mas é leve e funcional."
        )
        info.setObjectName("muted")
        info.setWordWrap(True)
        layout.addWidget(info)

        btn = QPushButton("Iniciar teste de velocidade")
        btn.setObjectName("primaryBtn")
        btn.clicked.connect(lambda: self.request_speed.emit())
        layout.addWidget(btn)

        self.speed_output = QTextEdit()
        self.speed_output.setReadOnly(True)
        layout.addWidget(self.speed_output)
        return w

    def _build_dns_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        form = QFormLayout()
        self.dns_query = QLineEdit("google.com")
        self.dns_mode = QComboBox()
        self.dns_mode.addItems(["Resolver hostname → IP", "Reverse lookup (IP → hostname)"])
        form.addRow("Consulta:", self.dns_query)
        form.addRow("Modo:", self.dns_mode)
        layout.addLayout(form)

        btn = QPushButton("Consultar DNS")
        btn.setObjectName("primaryBtn")
        btn.clicked.connect(self._do_dns)
        layout.addWidget(btn)

        self.dns_output = QTextEdit()
        self.dns_output.setReadOnly(True)
        layout.addWidget(self.dns_output)
        return w

    def _build_trace_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        form = QFormLayout()
        self.trace_target = QLineEdit("8.8.8.8")
        form.addRow("Destino:", self.trace_target)
        layout.addLayout(form)

        btn = QPushButton("Executar traceroute")
        btn.setObjectName("primaryBtn")
        btn.clicked.connect(self._do_trace)
        layout.addWidget(btn)

        self.trace_output = QTextEdit()
        self.trace_output.setReadOnly(True)
        layout.addWidget(self.trace_output)
        return w

    def _build_port_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        form = QFormLayout()
        self.port_host = QLineEdit("google.com")
        self.port_num = QSpinBox()
        self.port_num.setRange(1, 65535)
        self.port_num.setValue(443)
        form.addRow("Host:", self.port_host)
        form.addRow("Porta:", self.port_num)
        layout.addLayout(form)

        btn = QPushButton("Verificar porta TCP")
        btn.setObjectName("primaryBtn")
        btn.clicked.connect(self._do_port)
        layout.addWidget(btn)

        self.port_output = QTextEdit()
        self.port_output.setReadOnly(True)
        layout.addWidget(self.port_output)
        return w

    def _build_adapters_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        btn = QPushButton("Atualizar lista de adaptadores")
        btn.setObjectName("primaryBtn")
        btn.clicked.connect(self._refresh_adapters)
        layout.addWidget(btn)

        self.adapters_output = QTextEdit()
        self.adapters_output.setReadOnly(True)
        layout.addWidget(self.adapters_output)
        # Auto-load once
        self._refresh_adapters()
        return w

    # ---- actions ----
    def _do_ping(self) -> None:
        target = self.ping_target.text().strip()
        if not target:
            return
        self.ping_output.setPlainText("Executando…")
        self.request_ping.emit(target, self.ping_count.value())

    def _do_dns(self) -> None:
        q = self.dns_query.text().strip()
        if not q:
            return
        reverse = self.dns_mode.currentIndex() == 1
        self.dns_output.setPlainText("Consultando…")
        self.request_dns.emit(q, reverse)

    def _do_trace(self) -> None:
        t = self.trace_target.text().strip()
        if not t:
            return
        self.trace_output.setPlainText("Executando traceroute… (pode demorar)")
        self.request_traceroute.emit(t)

    def _do_port(self) -> None:
        host = self.port_host.text().strip()
        if not host:
            return
        self.port_output.setPlainText("Verificando…")
        self.request_port.emit(host, self.port_num.value())

    def _refresh_adapters(self) -> None:
        try:
            from app.network.adapters import get_network_adapters, get_default_gateway, get_io_counters
            adapters = get_network_adapters()
            gw = get_default_gateway()
            io = get_io_counters()
            lines = []
            if gw:
                lines.append(f"Gateway padrão (estimado): {gw}\n")
            lines.append("=== Contadores globais ===")
            lines.append(f"  Enviados : {io['bytes_sent']:,} bytes")
            lines.append(f"  Recebidos: {io['bytes_recv']:,} bytes")
            lines.append(f"  Erros in/out: {io['errin']} / {io['errout']}")
            lines.append("")
            for a in adapters:
                lines.append(f"▸ {a['name']}  [{'UP' if a['is_up'] else 'DOWN'}]")
                if a.get("speed_mbps"):
                    lines.append(f"    Velocidade: {a['speed_mbps']} Mbps")
                if a.get("mtu"):
                    lines.append(f"    MTU: {a['mtu']}")
                for addr in a.get("addresses", []):
                    lines.append(f"    {addr.get('family')}: {addr.get('address')}")
                lines.append(f"    TX/RX: {a.get('bytes_sent', 0):,} / {a.get('bytes_recv', 0):,} bytes")
                lines.append("")
            self.adapters_output.setPlainText("\n".join(lines))
        except Exception as e:
            self.adapters_output.setPlainText(f"Erro: {e}")

    # ---- result slots (called from main window) ----
    @Slot(dict)
    def show_ping_result(self, data: dict) -> None:
        lines = [
            f"Destino: {data.get('target')}",
            f"Pacotes: {data.get('count')}  |  Sucesso: {data.get('success_count')}",
            f"Perda: {data.get('packet_loss_pct')} %",
            f"Mín: {data.get('min_ms')} ms  |  Médio: {data.get('avg_ms')} ms  |  Máx: {data.get('max_ms')} ms",
            f"Jitter: {data.get('jitter_ms')} ms",
            "",
            "Detalhes:",
        ]
        for i, r in enumerate(data.get("raw", []), 1):
            if r.get("success"):
                lines.append(f"  #{i}: {r.get('latency_ms')} ms")
            else:
                lines.append(f"  #{i}: FALHA ({r.get('error')})")
        self.ping_output.setPlainText("\n".join(lines))

    @Slot(dict)
    def show_speed_result(self, data: dict) -> None:
        d = data.get("download", {})
        u = data.get("upload", {})
        lines = ["=== Resultado do teste de velocidade ===", ""]
        if d.get("success"):
            lines.append(f"Download: {d.get('mbps')} Mbps  ({d.get('bytes')} bytes em {d.get('duration')} s)")
        else:
            lines.append(f"Download: falhou — {d.get('error')}")
        if u.get("success"):
            lines.append(f"Upload  : {u.get('mbps')} Mbps  ({u.get('bytes')} bytes em {u.get('duration')} s)")
        else:
            lines.append(f"Upload  : falhou — {u.get('error')}")
        self.speed_output.setPlainText("\n".join(lines))

    @Slot(dict)
    def show_dns_result(self, data: dict) -> None:
        if data.get("reverse"):
            self.dns_output.setPlainText(
                f"IP: {data.get('query')}\nHostname: {data.get('hostname') or '(não encontrado)'}"
            )
        else:
            lines = [f"Hostname: {data.get('hostname')}"]
            if data.get("error"):
                lines.append(f"Erro: {data['error']}")
            else:
                lines.append("IPv4: " + (", ".join(data.get("ipv4") or ["—"])))
                lines.append("IPv6: " + (", ".join(data.get("ipv6") or ["—"])))
            self.dns_output.setPlainText("\n".join(lines))

    @Slot(list)
    def show_trace_result(self, hops: list) -> None:
        if not hops:
            self.trace_output.setPlainText("Nenhum hop retornado.")
            return
        lines = ["Hop  IP                    Latência"]
        lines.append("-" * 42)
        for h in hops:
            ip = h.get("ip") or "*"
            lat = f"{h.get('latency_ms')} ms" if h.get("latency_ms") is not None else (h.get("error") or "*")
            lines.append(f"{h.get('hop'):3d}  {ip:22s} {lat}")
        self.trace_output.setPlainText("\n".join(lines))

    @Slot(dict)
    def show_port_result(self, data: dict) -> None:
        if data.get("open"):
            self.port_output.setPlainText(
                f"Porta {data.get('port')} em {data.get('host')} está ABERTA\n"
                f"Latência de conexão: {data.get('latency_ms')} ms"
            )
        else:
            self.port_output.setPlainText(
                f"Porta {data.get('port')} em {data.get('host')} parece FECHADA ou filtrada\n"
                f"Detalhe: {data.get('error')}"
            )

    @Slot(str)
    def show_error(self, msg: str) -> None:
        # Generic error into currently visible-ish area
        self.ping_output.append(f"\n[Erro] {msg}")
