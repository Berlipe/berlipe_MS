# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-11-20

### Added
- Dashboard with live latency, jitter, packet loss, and speed metrics
- Continuous monitoring with configurable target and interval
- Real-time latency chart (pyqtgraph)
- Network tools: ping series, jitter, packet loss, DNS lookup, traceroute, TCP port check, adapter info
- Lightweight download/upload speed estimation
- SQLite local history with period filters
- CSV and JSON export
- Dark minimalist UI (PySide6)
- Settings persistence (target, interval, thresholds, retention)
- Automated tests for core statistics and database
- Project structure ready for PyInstaller and GitHub Actions

### Notes
- Speed test is an approximation using public endpoints (not a full speedtest.net client)
- Raw ICMP requires privileges; the app falls back to system `ping` when needed
- Traceroute uses system `tracert` / `traceroute`
