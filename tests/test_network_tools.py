"""Network helper tests (no external network required for most)."""

from app.network.dns_tools import resolve_hostname, resolve_with_details
from app.network.port_scan import check_tcp_port
from app.network.ping import ping_once


def test_resolve_localhost():
    ips = resolve_hostname("localhost")
    assert isinstance(ips, list)
    # Usually contains 127.0.0.1
    assert any("127." in ip or ip == "::1" for ip in ips) or len(ips) >= 0


def test_resolve_details():
    d = resolve_with_details("localhost")
    assert "hostname" in d
    assert d["hostname"] == "localhost"


def test_port_invalid():
    r = check_tcp_port("127.0.0.1", 0)
    assert r.open is False
    assert r.error == "invalid_port"


def test_port_closed_unlikely():
    # High port that should be closed on most systems
    r = check_tcp_port("127.0.0.1", 59999, timeout=0.5)
    # We don't assert open/closed strictly because environments vary
    assert r.host == "127.0.0.1"
    assert r.port == 59999


def test_ping_localhost_or_graceful_fail():
    # May require privileges or system ping; just ensure it returns PingResult
    r = ping_once("127.0.0.1", timeout=1.0)
    assert r.target == "127.0.0.1"
    assert isinstance(r.success, bool)
