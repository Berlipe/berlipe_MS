#!/usr/bin/env python3
"""berlip_MS — Professional Network Monitor entry point."""

from __future__ import annotations

import sys


def main() -> int:
    # High-DPI must be set before QApplication on some platforms
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QGuiApplication

    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("berlip_MS")
    app.setOrganizationName("berlip")
    app.setApplicationVersion("1.0.0")
    app.setStyle("Fusion")

    from app.ui.main_window import MainWindow

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
