"""
main_window.py — PyQt5 Dashboard for Memory Forensics Framework

A modern, dark-themed dashboard with:
  • Side navigation (Processes, Network, Credentials, Malware Scan)
  • Memory dump file loader
  • Main data table area for displaying forensic results
  • Background QThread worker for non-blocking Volatility scans
  • Status bar and header info
"""

import os
import traceback
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QFileDialog, QFrame,
    QHeaderView, QStackedWidget, QSizePolicy, QGraphicsDropShadowEffect,
    QAbstractItemView, QStatusBar, QProgressBar, QMessageBox, QApplication,
    QShortcut, QDialog
)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette, QLinearGradient, QPainter, QKeySequence

from core.vol_wrapper import VolatilityManager
from core.yara_scanner import YaraScanner


# ─── Color Palette ────────────────────────────────────────────────────────────
COLORS = {
    "bg_dark":        "#0B0E14",
    "bg_panel":       "#111621",
    "bg_card":        "#161B28",
    "bg_hover":       "#1C2333",
    "accent":         "#00E5A0",
    "accent_dim":     "#00C78A",
    "accent_glow":    "rgba(0, 229, 160, 0.15)",
    "text_primary":   "#E6EDF3",
    "text_secondary": "#7D8CA3",
    "text_muted":     "#4A5568",
    "border":         "#1E2A3A",
    "danger":         "#FF6B6B",
    "warning":        "#FFD93D",
    "info":           "#6CB4EE",
    "table_row_alt":  "#131925",
    "purple":         "#A78BFA",
}


# ─── Reusable Stylesheet Fragments ───────────────────────────────────────────
GLOBAL_STYLESHEET = f"""
    /* ── Base ─────────────────────────────────── */
    QMainWindow {{
        background-color: {COLORS['bg_dark']};
    }}

    /* ── Scroll bars ──────────────────────────── */
    QScrollBar:vertical {{
        background: {COLORS['bg_panel']};
        width: 8px;
        margin: 0;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {COLORS['border']};
        min-height: 30px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {COLORS['text_muted']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar:horizontal {{
        background: {COLORS['bg_panel']};
        height: 8px;
        margin: 0;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal {{
        background: {COLORS['border']};
        min-width: 30px;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {COLORS['text_muted']};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0;
    }}

    /* ── Tooltips ─────────────────────────────── */
    QToolTip {{
        background-color: {COLORS['bg_card']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        padding: 6px 10px;
        border-radius: 6px;
        font-size: 12px;
    }}
"""


# ═══════════════════════════════════════════════════════════════════════════════
#   WORKER  THREAD  — runs Volatility scans off the GUI thread
# ═══════════════════════════════════════════════════════════════════════════════
class VolWorker(QThread):
    """
    Background worker that executes a Volatility plugin via VolatilityManager.

    Signals
    -------
    finished : list
        Emitted with the parsed row data on success.
    error : str
        Emitted with an error message if the scan fails.
    """
    finished = pyqtSignal(list)
    error    = pyqtSignal(str)

    def __init__(self, dump_path: str, method_name: str, parent=None):
        super().__init__(parent)
        self.dump_path = dump_path
        self.method_name = method_name      # e.g. "run_pslist"

    def run(self):
        try:
            mgr = VolatilityManager(self.dump_path)
            method = getattr(mgr, self.method_name)
            rows = method()
            self.finished.emit(rows)
        except Exception as exc:
            self.error.emit(f"{exc}\n\n{traceback.format_exc()}")


class YaraWorker(QThread):
    """Background worker for automated YARA scanning."""
    finished = pyqtSignal(list)
    error    = pyqtSignal(str)

    def __init__(self, dump_path: str, parent=None):
        super().__init__(parent)
        self.dump_path = dump_path

    def run(self):
        try:
            scanner = YaraScanner()
            rows = scanner.auto_scan(self.dump_path)
            self.finished.emit(rows)
        except Exception as exc:
            self.error.emit(f"{exc}\n\n{traceback.format_exc()}")



# ═══════════════════════════════════════════════════════════════════════════════
#   NAV  BUTTON
# ═══════════════════════════════════════════════════════════════════════════════
class NavButton(QPushButton):
    """Custom navigation button for the sidebar."""

    def __init__(self, icon_char: str, label: str, parent=None):
        super().__init__(parent)
        self.icon_char = icon_char
        self.label = label
        self.setText(f"  {icon_char}   {label}")
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(48)
        self.setFont(QFont("Segoe UI", 11))
        self._apply_style(False)

    def _apply_style(self, active: bool):
        if active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['accent_glow']};
                    color: {COLORS['accent']};
                    border: none;
                    border-left: 3px solid {COLORS['accent']};
                    border-radius: 0px;
                    text-align: left;
                    padding-left: 16px;
                    font-weight: 600;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLORS['text_secondary']};
                    border: none;
                    border-left: 3px solid transparent;
                    border-radius: 0px;
                    text-align: left;
                    padding-left: 16px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['bg_hover']};
                    color: {COLORS['text_primary']};
                }}
            """)

    def set_active(self, active: bool):
        self.setChecked(active)
        self._apply_style(active)


# ═══════════════════════════════════════════════════════════════════════════════
#   STAT  CARD
# ═══════════════════════════════════════════════════════════════════════════════
class StatCard(QFrame):
    """Small KPI card shown in the dashboard header."""

    def __init__(self, title: str, value: str, color: str, parent=None):
        super().__init__(parent)
        self.setFixedHeight(90)
        self.setMinimumWidth(180)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(4)

        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Segoe UI", 10))
        lbl_title.setStyleSheet(f"color: {COLORS['text_secondary']}; border: none;")

        lbl_value = QLabel(value)
        lbl_value.setFont(QFont("Segoe UI Semibold", 22))
        lbl_value.setStyleSheet(f"color: {color}; border: none;")

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)

        # Subtle glow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(color))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)

    def update_value(self, value: str):
        """Update the displayed value."""
        layout = self.layout()
        lbl_value = layout.itemAt(1).widget()
        if lbl_value:
            lbl_value.setText(value)


# ═══════════════════════════════════════════════════════════════════════════════
#   PAGE  WIDGET  (one per nav section)
# ═══════════════════════════════════════════════════════════════════════════════
class ForensicsPage(QWidget):
    """A page that contains a header label and a data table."""

    COLUMN_DEFS = {
        "Processes":        ["PID", "Name", "PPID", "Threads", "Handles", "Session", "Create Time", "Exit Time"],
        "Loaded DLLs":      ["PID", "Process", "Base Address", "Size", "DLL Name", "Path"],
        "Network":          ["Protocol", "Local Address", "Local Port", "Remote Address", "Remote Port", "State", "PID", "Owner"],
        "Credentials & Keys": ["User / Source", "RID / PID", "Hash / Key", "Extra", "Type"],
        "Malware Scan":     ["PID", "Process", "Start VPN", "End VPN", "Protection", "Hexdump", "Disasm"],
        "YARA Scan":        ["Rule", "PID", "Process", "Offset", "Match"],
    }

    def __init__(self, page_name: str, parent=None):
        super().__init__(parent)
        self.page_name = page_name
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # ── Section header ────────────────────────
        header = QLabel(page_name)
        header.setFont(QFont("Segoe UI Semibold", 16))
        header.setStyleSheet(f"color: {COLORS['text_primary']}; padding: 4px 0;")
        layout.addWidget(header)

        # ── Subtitle ─────────────────────────────
        descriptions = {
            "Processes":          "Active and terminated processes extracted from the memory image.",
            "Loaded DLLs":        "Dynamic-Link Libraries loaded by each process in the memory image.",
            "Network":            "Recovered network sockets, connections, and listening ports.",
            "Credentials & Keys": "Password hashes, cached credentials, and encryption keys detected in memory.",
            "Malware Scan":       "Suspicious memory regions with PAGE_EXECUTE_READWRITE permissions detected by malfind.",
            "YARA Scan":          "Malware signature matches found using Neo23x0 and custom YARA rules.",
        }
        subtitle = QLabel(descriptions.get(page_name, ""))
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet(f"color: {COLORS['text_muted']};")
        layout.addWidget(subtitle)

        # ── Data table ────────────────────────────
        self.table = QTableWidget()
        cols = self.COLUMN_DEFS.get(page_name, ["Column 1", "Column 2"])
        self.table.setColumnCount(len(cols))
        self.table.setHorizontalHeaderLabels(cols)
        self.table.setRowCount(0)

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setFocusPolicy(Qt.NoFocus)

        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['bg_card']};
                alternate-background-color: {COLORS['table_row_alt']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                gridline-color: transparent;
                font-size: 12px;
                selection-background-color: {COLORS['accent_glow']};
                selection-color: {COLORS['accent']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['bg_panel']};
                color: {COLORS['text_secondary']};
                font-weight: 600;
                font-size: 11px;
                border: none;
                border-bottom: 2px solid {COLORS['border']};
                padding: 8px 12px;
            }}
            QTableWidget::item {{
                padding: 6px 12px;
                border-bottom: 1px solid {COLORS['bg_panel']};
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['accent_glow']};
            }}
        """)

        layout.addWidget(self.table)

        # ── Ctrl+C copy support ───────────────────
        shortcut = QShortcut(QKeySequence.Copy, self.table)
        shortcut.activated.connect(self._copy_selection)

    def _copy_selection(self):
        """Copy selected cells to clipboard as tab-separated text."""
        selection = self.table.selectedIndexes()
        if not selection:
            return

        # Group by row
        rows_dict: dict[int, dict[int, str]] = {}
        for idx in selection:
            rows_dict.setdefault(idx.row(), {})[idx.column()] = idx.data() or ""

        lines = []
        for row_key in sorted(rows_dict):
            cols = rows_dict[row_key]
            lines.append("\t".join(cols[c] for c in sorted(cols)))

        QApplication.clipboard().setText("\n".join(lines))

    def clear(self):
        """Remove all rows from the table."""
        self.table.setRowCount(0)

    def populate(self, rows: list[list[str]]):
        """Fill the table with data rows."""
        self.table.setRowCount(len(rows))
        for r, row_data in enumerate(rows):
            for c, cell in enumerate(row_data):
                item = QTableWidgetItem(str(cell))
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.table.setItem(r, c, item)


# ═══════════════════════════════════════════════════════════════════════════════
#   SCAN  OPTIONS  DIALOG
# ═══════════════════════════════════════════════════════════════════════════════
class ScanOptionsDialog(QDialog):
    """Dialog shown after loading a dump — lets user add custom YARA rules before scanning."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Scan Options")
        self.setFixedSize(480, 260)
        self.custom_rule_added = False

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_panel']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # Title
        title = QLabel("🛡  Scan Options")
        title.setFont(QFont("Segoe UI Semibold", 15))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(title)

        # Description
        desc = QLabel("Choose how to start the analysis pipeline.\n"
                      "You can optionally add a custom YARA rule file before scanning.")
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet(f"color: {COLORS['text_secondary']};")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Status label (for custom rule feedback)
        self.lbl_status = QLabel("")
        self.lbl_status.setFont(QFont("Segoe UI", 9))
        self.lbl_status.setStyleSheet(f"color: {COLORS['accent']};")
        self.lbl_status.setWordWrap(True)
        layout.addWidget(self.lbl_status)

        layout.addStretch()

        # Buttons row
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        btn_style_secondary = f"""
            QPushButton {{
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                padding: 10px 18px;
                font-weight: 600;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
                border-color: {COLORS['purple']};
            }}
        """

        btn_style_primary = f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: {COLORS['bg_dark']};
                border: none;
                border-radius: 10px;
                padding: 10px 22px;
                font-weight: 700;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_dim']};
            }}
        """

        self.btn_custom = QPushButton("🔍  Add Custom YARA Rule")
        self.btn_custom.setCursor(Qt.PointingHandCursor)
        self.btn_custom.setStyleSheet(btn_style_secondary)
        self.btn_custom.clicked.connect(self._add_custom_rule)
        btn_layout.addWidget(self.btn_custom)

        self.btn_start = QPushButton("▶  Start Scan")
        self.btn_start.setCursor(Qt.PointingHandCursor)
        self.btn_start.setStyleSheet(btn_style_primary)
        self.btn_start.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_start)

        layout.addLayout(btn_layout)

    def _add_custom_rule(self):
        """Open the Rule Source dialog for URL or local file."""
        dialog = RuleSourceDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.custom_rule_added = True
            self.lbl_status.setStyleSheet(f"color: {COLORS['accent']};")
            self.lbl_status.setText(f"✅  Added: {dialog.added_filename}")


# ═══════════════════════════════════════════════════════════════════════════════
#   RULE  SOURCE  DIALOG  (URL or Local File)
# ═══════════════════════════════════════════════════════════════════════════════
class RuleSourceDialog(QDialog):
    """Sub-dialog for adding a custom YARA rule from a URL or local file."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Custom YARA Rule")
        self.setFixedSize(520, 320)
        self.added_filename = ""

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_panel']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
            QLineEdit {{
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 12px;
                font-family: 'Segoe UI';
            }}
            QLineEdit:focus {{
                border-color: {COLORS['accent']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        # Title
        title = QLabel("🔍  Add Custom YARA Rule")
        title.setFont(QFont("Segoe UI Semibold", 14))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(title)

        # URL input
        url_label = QLabel("Paste a URL to a .yar rule file:")
        url_label.setFont(QFont("Segoe UI", 10))
        url_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        layout.addWidget(url_label)

        from PyQt5.QtWidgets import QLineEdit
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://raw.githubusercontent.com/.../rule.yar")
        layout.addWidget(self.url_input)

        # OR separator
        or_label = QLabel("— OR —")
        or_label.setFont(QFont("Segoe UI Semibold", 10))
        or_label.setStyleSheet(f"color: {COLORS['text_muted']};")
        or_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(or_label)

        # Browse button
        btn_style = f"""
            QPushButton {{
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                padding: 10px 18px;
                font-weight: 600;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
                border-color: {COLORS['info']};
            }}
        """

        self.btn_browse = QPushButton("📂  Browse Local File")
        self.btn_browse.setCursor(Qt.PointingHandCursor)
        self.btn_browse.setStyleSheet(btn_style)
        self.btn_browse.clicked.connect(self._browse_file)
        layout.addWidget(self.btn_browse)

        # Selected file label
        self.lbl_selected = QLabel("")
        self.lbl_selected.setFont(QFont("Segoe UI", 9))
        self.lbl_selected.setStyleSheet(f"color: {COLORS['text_muted']};")
        self.lbl_selected.setWordWrap(True)
        layout.addWidget(self.lbl_selected)

        layout.addStretch()

        # Add Rule button
        btn_add_style = f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: {COLORS['bg_dark']};
                border: none;
                border-radius: 10px;
                padding: 10px 22px;
                font-weight: 700;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_dim']};
            }}
        """

        self.btn_add = QPushButton("✅  Add Rule")
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.setStyleSheet(btn_add_style)
        self.btn_add.clicked.connect(self._add_rule)
        layout.addWidget(self.btn_add)

        self._selected_file = None

    def _browse_file(self):
        """Open file dialog for local .yar file."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select YARA Rule File", "",
            "YARA Rules (*.yar *.yara);;All Files (*)"
        )
        if path:
            self._selected_file = path
            self.url_input.clear()
            self.lbl_selected.setStyleSheet(f"color: {COLORS['info']};")
            self.lbl_selected.setText(f"📄  {os.path.basename(path)}")

    def _add_rule(self):
        """Validate the source (URL or file) and add the rule."""
        url_text = self.url_input.text().strip()

        # Determine the source
        if url_text:
            source = url_text
        elif self._selected_file:
            source = self._selected_file
        else:
            QMessageBox.warning(self, "No Source",
                                "Please enter a URL or select a local file.")
            return

        try:
            scanner = YaraScanner()
            dest = scanner.add_custom_rule(source)
            self.added_filename = os.path.basename(dest)
            self.accept()
        except ValueError as e:
            QMessageBox.critical(self, "YARA Rule Error", str(e))


# ═══════════════════════════════════════════════════════════════════════════════
#   MAIN  WINDOW
# ═══════════════════════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    """Primary application window — Memory Forensics Dashboard."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MemForensics — Memory Forensics & Volatile Data Analysis")
        self.setMinimumSize(1180, 720)
        self.resize(1360, 820)
        self.setStyleSheet(GLOBAL_STYLESHEET)

        self.loaded_dump_path: str | None = None
        self._worker: VolWorker | None = None       # keep a ref so it doesn't get GC'd
        self._yara_worker: YaraWorker | None = None
        self._malfind_rows: list = []                # preserved for YARA append

        # ── Central widget ────────────────────────
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Sidebar ───────────────────────────────
        root_layout.addWidget(self._build_sidebar())

        # ── Right pane (header + pages) ───────────
        right_pane = QVBoxLayout()
        right_pane.setContentsMargins(28, 22, 28, 18)
        right_pane.setSpacing(18)

        right_pane.addWidget(self._build_top_bar())
        right_pane.addLayout(self._build_stat_cards())
        right_pane.addWidget(self._build_pages(), stretch=1)

        root_layout.addLayout(right_pane, stretch=1)

        # ── Status bar ────────────────────────────
        self._build_status_bar()

        # Select first nav item
        self._on_nav_clicked(0)

    # ── SIDEBAR ───────────────────────────────────────────────────────────────
    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setFixedWidth(230)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_panel']};
                border-right: 1px solid {COLORS['border']};
            }}
        """)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Brand ─────────────────────────────────
        brand_frame = QFrame()
        brand_frame.setFixedHeight(72)
        brand_frame.setStyleSheet(f"""
            QFrame {{
                border-bottom: 1px solid {COLORS['border']};
                border-right: none;
            }}
        """)
        brand_layout = QHBoxLayout(brand_frame)
        brand_layout.setContentsMargins(20, 0, 20, 0)

        logo = QLabel("🧠")
        logo.setFont(QFont("Segoe UI Emoji", 22))
        logo.setStyleSheet("border: none;")

        title = QLabel("MemForensics")
        title.setFont(QFont("Segoe UI Semibold", 15))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; border: none;")

        brand_layout.addWidget(logo)
        brand_layout.addWidget(title)
        brand_layout.addStretch()

        layout.addWidget(brand_frame)

        # ── Section label ─────────────────────────
        section_label = QLabel("   ANALYSIS")
        section_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        section_label.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            padding: 18px 0 6px 14px;
            letter-spacing: 1.5px;
            border: none;
        """)
        layout.addWidget(section_label)

        # ── Nav buttons ───────────────────────────
        nav_items = [
            ("⚙", "Processes"),
            ("📦", "Loaded DLLs"),
            ("🌐", "Network"),
            ("🔑", "Credentials & Keys"),
            ("🛡", "Malware Scan"),
            ("🔍", "YARA Scan"),
        ]

        self.nav_buttons: list[NavButton] = []
        for idx, (icon, label) in enumerate(nav_items):
            btn = NavButton(icon, label)
            btn.clicked.connect(lambda checked, i=idx: self._on_nav_clicked(i))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)

        layout.addStretch()

        # ── Footer ────────────────────────────────
        footer_label = QLabel("  v1.0.0  •  Final")
        footer_label.setFont(QFont("Segoe UI", 9))
        footer_label.setStyleSheet(f"color: {COLORS['text_muted']}; padding: 14px; border: none;")
        layout.addWidget(footer_label)

        return sidebar

    # ── TOP BAR ───────────────────────────────────────────────────────────────
    def _build_top_bar(self) -> QFrame:
        bar = QFrame()
        bar.setFixedHeight(52)
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(0, 0, 0, 0)

        # File info
        self.lbl_dump_info = QLabel("No memory dump loaded")
        self.lbl_dump_info.setFont(QFont("Segoe UI", 11))
        self.lbl_dump_info.setStyleSheet(f"color: {COLORS['text_secondary']};")
        bar_layout.addWidget(self.lbl_dump_info)

        bar_layout.addStretch()

        # Load button
        self.btn_load = QPushButton("  📂  Load Memory Dump")
        self.btn_load.setCursor(Qt.PointingHandCursor)
        self.btn_load.setFixedHeight(40)
        self.btn_load.setFont(QFont("Segoe UI Semibold", 11))
        self.btn_load.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: {COLORS['bg_dark']};
                border: none;
                border-radius: 10px;
                padding: 0 22px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_dim']};
            }}
            QPushButton:pressed {{
                background-color: #00B07A;
            }}
        """)
        self.btn_load.clicked.connect(self._load_dump)
        bar_layout.addWidget(self.btn_load)


        return bar

    # ── STAT CARDS ────────────────────────────────────────────────────────────
    def _build_stat_cards(self) -> QHBoxLayout:
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        self.card_processes = StatCard("Processes", "—", COLORS['accent'])
        self.card_dlls      = StatCard("Loaded DLLs", "—", "#E879F9")
        self.card_network   = StatCard("Connections", "—", COLORS['info'])
        self.card_creds     = StatCard("Creds & Keys", "—", COLORS['warning'])
        self.card_malware   = StatCard("Malfind Hits", "—", COLORS['danger'])
        self.card_yara      = StatCard("YARA Matches", "—", COLORS['purple'])

        for card in (self.card_processes, self.card_dlls, self.card_network, self.card_creds, self.card_malware, self.card_yara):
            cards_layout.addWidget(card)

        return cards_layout

    # ── STACKED PAGES ─────────────────────────────────────────────────────────
    def _build_pages(self) -> QStackedWidget:
        self.pages = QStackedWidget()
        self.pages.setStyleSheet("background: transparent;")

        self.page_processes  = ForensicsPage("Processes")
        self.page_dlls       = ForensicsPage("Loaded DLLs")
        self.page_network    = ForensicsPage("Network")
        self.page_creds      = ForensicsPage("Credentials & Keys")
        self.page_malware    = ForensicsPage("Malware Scan")
        self.page_yara       = ForensicsPage("YARA Scan")

        self.pages.addWidget(self.page_processes)
        self.pages.addWidget(self.page_dlls)
        self.pages.addWidget(self.page_network)
        self.pages.addWidget(self.page_creds)
        self.pages.addWidget(self.page_malware)
        self.pages.addWidget(self.page_yara)

        return self.pages

    # ── STATUS BAR ────────────────────────────────────────────────────────────
    def _build_status_bar(self):
        status = QStatusBar()
        status.setStyleSheet(f"""
            QStatusBar {{
                background-color: {COLORS['bg_panel']};
                color: {COLORS['text_muted']};
                border-top: 1px solid {COLORS['border']};
                font-size: 11px;
                padding: 2px 12px;
            }}
        """)
        self.progress = QProgressBar()
        self.progress.setFixedWidth(180)
        self.progress.setFixedHeight(14)
        self.progress.setVisible(False)
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 7px;
                text-align: center;
                font-size: 9px;
                color: {COLORS['text_secondary']};
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['accent']};
                border-radius: 6px;
            }}
        """)
        status.addPermanentWidget(self.progress)
        status.showMessage("Ready")
        self.setStatusBar(status)

    # ══════════════════════════════════════════════════════════════════════════
    #   SLOTS
    # ══════════════════════════════════════════════════════════════════════════
    def _on_nav_clicked(self, index: int):
        """Switch active page and highlight the nav button."""
        for i, btn in enumerate(self.nav_buttons):
            btn.set_active(i == index)
        self.pages.setCurrentIndex(index)

    def _load_dump(self):
        """Open file dialog to select a memory dump, then show scan options."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Memory Dump",
            "",
            "Memory Dumps (*.raw *.mem *.dmp *.vmem *.lime *.img);;All Files (*)"
        )
        if not path:
            return

        self.loaded_dump_path = path
        fname = os.path.basename(path)
        size_mb = os.path.getsize(path) / (1024 * 1024)
        self.lbl_dump_info.setText(f"📄  {fname}  ({size_mb:,.1f} MB)")
        self.lbl_dump_info.setStyleSheet(f"color: {COLORS['accent']};")
        self.statusBar().showMessage(f"Loaded: {path}")

        # Clear any old data
        self.page_processes.clear()
        self.page_dlls.clear()
        self.page_network.clear()
        self.page_creds.clear()
        self.page_malware.clear()
        self.page_yara.clear()
        for card in (self.card_processes, self.card_dlls, self.card_network, self.card_creds, self.card_malware, self.card_yara):
            card.update_value("—")

        # Show scan options dialog before starting the pipeline
        dialog = ScanOptionsDialog(self)
        result = dialog.exec_()

        if result == QDialog.Accepted:
            self._run_pslist()

    # ══════════════════════════════════════════════════════════════════════════
    #   BACKGROUND  VOLATILITY  SCANS  (7-step pipeline)
    # ══════════════════════════════════════════════════════════════════════════

    def _start_scan(self, method_name: str, status_msg: str, on_done, on_error):
        """Generic helper to launch a VolWorker for any scan method."""
        self.btn_load.setEnabled(False)
        self.progress.setRange(0, 0)
        self.progress.setVisible(True)
        self.statusBar().showMessage(status_msg)

        self._worker = VolWorker(self.loaded_dump_path, method_name)
        self._worker.finished.connect(on_done)
        self._worker.error.connect(on_error)
        self._worker.start()

    def _finish_pipeline(self):
        """Common cleanup when the full pipeline ends."""
        self.progress.setVisible(False)
        self.progress.setRange(0, 100)
        self.btn_load.setEnabled(True)

    # ── 1. PSLIST ─────────────────────────────────────────────────────────────
    def _run_pslist(self):
        self._start_scan("run_pslist", "⏳  [1/7] Process Extraction (pslist) …",
                         self._on_pslist_done, self._on_pslist_error)

    def _on_pslist_done(self, rows: list):
        self.page_processes.populate(rows)
        self.card_processes.update_value(str(len(rows)))
        self._on_nav_clicked(0)
        self._run_dlllist()

    def _on_pslist_error(self, msg: str):
        self.statusBar().showMessage("⚠  pslist failed — continuing pipeline …")
        self._run_dlllist()

    # ── 2. DLLLIST ────────────────────────────────────────────────────────────
    def _run_dlllist(self):
        self._start_scan("run_dlllist", "⏳  [2/7] DLL Extraction (dlllist) …",
                         self._on_dlllist_done, self._on_dlllist_error)

    def _on_dlllist_done(self, rows: list):
        self.page_dlls.populate(rows)
        self.card_dlls.update_value(str(len(rows)))
        self._run_netscan()

    def _on_dlllist_error(self, msg: str):
        self.card_dlls.update_value("0")
        self.statusBar().showMessage("⚠  dlllist failed — continuing pipeline …")
        self._run_netscan()

    # ── 3. NETSCAN ────────────────────────────────────────────────────────────
    def _run_netscan(self):
        self._start_scan("run_netscan", "⏳  [3/7] Network Socket Recovery (netscan) …",
                         self._on_netscan_done, self._on_netscan_error)

    def _on_netscan_done(self, rows: list):
        self.page_network.populate(rows)
        self.card_network.update_value(str(len(rows)))
        self._run_malfind()

    def _on_netscan_error(self, msg: str):
        self.card_network.update_value("0")
        self.statusBar().showMessage("⚠  netscan failed — continuing pipeline …")
        self._run_malfind()

    # ── 4. MALFIND ────────────────────────────────────────────────────────────
    def _run_malfind(self):
        self._start_scan("run_malfind", "⏳  [4/7] Injection Detection (malfind) …",
                         self._on_malfind_done, self._on_malfind_error)

    def _on_malfind_done(self, rows: list):
        self._malfind_rows = rows
        self.page_malware.populate(rows)
        self.card_malware.update_value(str(len(rows)))
        self._run_hashdump()

    def _on_malfind_error(self, msg: str):
        self._malfind_rows = []
        self.card_malware.update_value("0")
        self.statusBar().showMessage("⚠  malfind failed — continuing pipeline …")
        self._run_hashdump()

    # ── 5. HASHDUMP ───────────────────────────────────────────────────────────
    def _run_hashdump(self):
        self._start_scan("run_hashdump", "⏳  [5/7] Credential Recovery (hashdump) …",
                         self._on_hashdump_done, self._on_hashdump_error)

    def _on_hashdump_done(self, rows: list):
        self._hashdump_rows = rows
        self.page_creds.populate(rows)
        self.card_creds.update_value(str(len(rows)))
        self._run_encryption_scan()

    def _on_hashdump_error(self, msg: str):
        self._hashdump_rows = []
        self.card_creds.update_value("0")
        self.statusBar().showMessage("⚠  hashdump skipped — continuing pipeline …")
        self._run_encryption_scan()

    # ── 6. ENCRYPTION SCAN ────────────────────────────────────────────────────
    def _run_encryption_scan(self):
        self._start_scan("run_encryption_scan", "⏳  [6/7] Encryption Key Detection …",
                         self._on_encryption_done, self._on_encryption_error)

    def _on_encryption_done(self, rows: list):
        # Append encryption results to existing hashdump rows in the Credentials & Keys table
        if rows:
            existing = getattr(self, '_hashdump_rows', [])
            combined = existing + rows
            self.page_creds.populate(combined)
            self.card_creds.update_value(str(len(combined)))
        self._run_auto_yarascan()

    def _on_encryption_error(self, msg: str):
        self.statusBar().showMessage("⚠  Encryption scan skipped — continuing pipeline …")
        self._run_auto_yarascan()

    # ── 7. AUTO YARA SCAN ─────────────────────────────────────────────────────
    def _run_auto_yarascan(self):
        """Launch automated YARA scan with Neo23x0 + local rules."""
        self.btn_load.setEnabled(False)
        self.progress.setRange(0, 0)
        self.progress.setVisible(True)
        self.statusBar().showMessage(
            "⏳  [7/7] YARA Signature Scan (Neo23x0 rules) …"
        )

        self._yara_worker = YaraWorker(self.loaded_dump_path)
        self._yara_worker.finished.connect(self._on_yarascan_done)
        self._yara_worker.error.connect(self._on_yarascan_error)
        self._yara_worker.start()

    def _on_yarascan_done(self, rows: list):
        """Populate the dedicated YARA Scan page with YARA matches."""
        self._finish_pipeline()

        # Populate the YARA page directly — rows are already [Rule, PID, Process, Offset, Match]
        self.page_yara.populate(rows)
        self.card_yara.update_value(str(len(rows)))

        malfind_count = len(self._malfind_rows)
        yara_count = len(rows)
        self.statusBar().showMessage(
            f"✅  All 7 scans complete — {malfind_count} injections (malfind) + "
            f"{yara_count} YARA signature matches"
        )

    def _on_yarascan_error(self, msg: str):
        self._finish_pipeline()
        self.statusBar().showMessage(
            "✅  Pipeline complete (YARA scan skipped — see status for details)"
        )
