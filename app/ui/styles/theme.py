"""Dark theme stylesheet and palette helpers."""

from app.core.constants import (
    COLOR_BG,
    COLOR_SURFACE,
    COLOR_SURFACE_2,
    COLOR_BORDER,
    COLOR_TEXT,
    COLOR_TEXT_DIM,
    COLOR_ACCENT,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_DANGER,
)

DARK_STYLESHEET = f"""
/* ===== Global ===== */
QWidget {{
    background-color: {COLOR_BG};
    color: {COLOR_TEXT};
    font-family: "Segoe UI", "Ubuntu", "Cantarell", "Noto Sans", sans-serif;
    font-size: 13px;
}}

QMainWindow {{
    background-color: {COLOR_BG};
}}

/* ===== Sidebar ===== */
#sidebar {{
    background-color: {COLOR_SURFACE};
    border-right: 1px solid {COLOR_BORDER};
}}

#sidebar QPushButton {{
    background-color: transparent;
    border: none;
    border-radius: 8px;
    padding: 10px 14px;
    text-align: left;
    color: {COLOR_TEXT_DIM};
    font-size: 13px;
    font-weight: 500;
}}

#sidebar QPushButton:hover {{
    background-color: {COLOR_SURFACE_2};
    color: {COLOR_TEXT};
}}

#sidebar QPushButton:checked {{
    background-color: {COLOR_ACCENT};
    color: #ffffff;
}}

#sidebarTitle {{
    color: {COLOR_TEXT};
    font-size: 16px;
    font-weight: 700;
    padding: 18px 16px 8px 16px;
}}

#sidebarSubtitle {{
    color: {COLOR_TEXT_DIM};
    font-size: 11px;
    padding: 0 16px 12px 16px;
}}

/* ===== Cards ===== */
.card, QFrame#card {{
    background-color: {COLOR_SURFACE};
    border: 1px solid {COLOR_BORDER};
    border-radius: 10px;
}}

QLabel#cardTitle {{
    color: {COLOR_TEXT_DIM};
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

QLabel#cardValue {{
    color: {COLOR_TEXT};
    font-size: 22px;
    font-weight: 700;
}}

QLabel#cardUnit {{
    color: {COLOR_TEXT_DIM};
    font-size: 12px;
}}

/* ===== Buttons ===== */
QPushButton {{
    background-color: {COLOR_SURFACE_2};
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    padding: 7px 14px;
    color: {COLOR_TEXT};
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: #252b38;
    border-color: #3a4255;
}}

QPushButton:pressed {{
    background-color: #1a1f2a;
}}

QPushButton:disabled {{
    color: #555b6b;
    background-color: {COLOR_SURFACE};
}}

QPushButton#primaryBtn {{
    background-color: {COLOR_ACCENT};
    border: none;
    color: #ffffff;
}}

QPushButton#primaryBtn:hover {{
    background-color: #2563eb;
}}

QPushButton#dangerBtn {{
    background-color: transparent;
    border: 1px solid {COLOR_DANGER};
    color: {COLOR_DANGER};
}}

QPushButton#dangerBtn:hover {{
    background-color: rgba(239, 68, 68, 0.15);
}}

QPushButton#successBtn {{
    background-color: {COLOR_SUCCESS};
    border: none;
    color: #ffffff;
}}

/* ===== Inputs ===== */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: {COLOR_SURFACE_2};
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    padding: 6px 10px;
    color: {COLOR_TEXT};
    selection-background-color: {COLOR_ACCENT};
}}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border-color: {COLOR_ACCENT};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLOR_SURFACE};
    border: 1px solid {COLOR_BORDER};
    selection-background-color: {COLOR_ACCENT};
    color: {COLOR_TEXT};
}}

/* ===== Tables ===== */
QTableWidget, QTableView {{
    background-color: {COLOR_SURFACE};
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
    gridline-color: {COLOR_BORDER};
    selection-background-color: rgba(59, 130, 246, 0.25);
    selection-color: {COLOR_TEXT};
}}

QHeaderView::section {{
    background-color: {COLOR_SURFACE_2};
    color: {COLOR_TEXT_DIM};
    padding: 6px 10px;
    border: none;
    border-bottom: 1px solid {COLOR_BORDER};
    font-weight: 600;
    font-size: 11px;
}}

QTableWidget::item {{
    padding: 4px 8px;
}}

/* ===== Tabs / Scroll ===== */
QScrollArea {{
    border: none;
    background: transparent;
}}

QScrollBar:vertical {{
    background: {COLOR_SURFACE};
    width: 10px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: #3a4255;
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

/* ===== Status bar ===== */
QStatusBar {{
    background-color: {COLOR_SURFACE};
    border-top: 1px solid {COLOR_BORDER};
    color: {COLOR_TEXT_DIM};
    font-size: 12px;
}}

/* ===== Group boxes ===== */
QGroupBox {{
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 8px;
    font-weight: 600;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: {COLOR_TEXT_DIM};
}}

/* ===== Progress ===== */
QProgressBar {{
    background-color: {COLOR_SURFACE_2};
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: {COLOR_ACCENT};
    border-radius: 4px;
}}

/* ===== Labels ===== */
QLabel#sectionTitle {{
    font-size: 18px;
    font-weight: 700;
    color: {COLOR_TEXT};
}}

QLabel#muted {{
    color: {COLOR_TEXT_DIM};
}}
"""
