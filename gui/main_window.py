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
    QShortcut
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
        "Processes": ["PID", "Name", "PPID", "Threads", "Handles", "Session", "Create Time", "Exit Time"],
        "Network":   ["Protocol", "Local Address", "Local Port", "Remote Address", "Remote Port", "State", "PID", "Owner"],
        "Credentials": ["User", "RID", "LM Hash", "NTLM Hash"],
        "Malware Scan": ["PID", "Process", "Start VPN", "End VPN", "Protection", "Hexdump", "Disasm"],
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
            "Processes":    "Active and terminated processes extracted from the memory image.",
            "Network":      "Recovered network sockets, connections, and listening ports.",
            "Credentials":  "Encryption keys, passwords, and tokens detected in memory.",
            "Malware Scan": "YARA rule matches and malware indicators found in process memory.",
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
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
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
            ("🌐", "Network"),
            ("🔑", "Credentials"),
            ("🛡", "Malware Scan"),
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
        self.card_network   = StatCard("Connections", "—", COLORS['info'])
        self.card_creds     = StatCard("Credentials", "—", COLORS['warning'])
        self.card_malware   = StatCard("Malware Hits", "—", COLORS['danger'])

        for card in (self.card_processes, self.card_network, self.card_creds, self.card_malware):
            cards_layout.addWidget(card)

        return cards_layout

    # ── STACKED PAGES ─────────────────────────────────────────────────────────
    def _build_pages(self) -> QStackedWidget:
        self.pages = QStackedWidget()
        self.pages.setStyleSheet("background: transparent;")

        self.page_processes  = ForensicsPage("Processes")
        self.page_network    = ForensicsPage("Network")
        self.page_creds      = ForensicsPage("Credentials")
        self.page_malware    = ForensicsPage("Malware Scan")

        self.pages.addWidget(self.page_processes)
        self.pages.addWidget(self.page_network)
        self.pages.addWidget(self.page_creds)
        self.pages.addWidget(self.page_malware)

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
        """Open file dialog to select a memory dump, then kick off pslist scan."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Memory Dump",
            "",
            "Memory Dumps (*.raw *.mem *.dmp *.vmem *.lime *.img);;All Files (*)"
        )
        if path:
            self.loaded_dump_path = path
            fname = os.path.basename(path)
            size_mb = os.path.getsize(path) / (1024 * 1024)
            self.lbl_dump_info.setText(f"📄  {fname}  ({size_mb:,.1f} MB)")
            self.lbl_dump_info.setStyleSheet(f"color: {COLORS['accent']};")
            self.statusBar().showMessage(f"Loaded: {path}")

            # Clear any old data
            self.page_processes.clear()
            self.page_network.clear()
            self.page_creds.clear()
            self.page_malware.clear()
            for card in (self.card_processes, self.card_network, self.card_creds, self.card_malware):
                card.update_value("—")

            # Start the background pslist scan
            self._run_pslist()

    # ══════════════════════════════════════════════════════════════════════════
    #   BACKGROUND  VOLATILITY  SCANS  (5-step pipeline)
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
        self._start_scan("run_pslist", "⏳  [1/5] Process Extraction (pslist) …",
                         self._on_pslist_done, self._on_pslist_error)

    def _on_pslist_done(self, rows: list):
        self.page_processes.populate(rows)
        self.card_processes.update_value(str(len(rows)))
        self._on_nav_clicked(0)
        self._run_netscan()

    def _on_pslist_error(self, msg: str):
        self.statusBar().showMessage("⚠  pslist failed — continuing pipeline …")
        self._run_netscan()

    # ── 2. NETSCAN ────────────────────────────────────────────────────────────
    def _run_netscan(self):
        self._start_scan("run_netscan", "⏳  [2/5] Network Socket Recovery (netscan) …",
                         self._on_netscan_done, self._on_netscan_error)

    def _on_netscan_done(self, rows: list):
        self.page_network.populate(rows)
        self.card_network.update_value(str(len(rows)))
        self._run_malfind()

    def _on_netscan_error(self, msg: str):
        self.card_network.update_value("0")
        self.statusBar().showMessage("⚠  netscan failed — continuing pipeline …")
        self._run_malfind()

    # ── 3. MALFIND ────────────────────────────────────────────────────────────
    def _run_malfind(self):
        self._start_scan("run_malfind", "⏳  [3/5] Injection Detection (malfind) …",
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

    # ── 4. HASHDUMP ───────────────────────────────────────────────────────────
    def _run_hashdump(self):
        self._start_scan("run_hashdump", "⏳  [4/5] Credential Recovery (hashdump) …",
                         self._on_hashdump_done, self._on_hashdump_error)

    def _on_hashdump_done(self, rows: list):
        self.page_creds.populate(rows)
        self.card_creds.update_value(str(len(rows)))
        self._run_auto_yarascan()

    def _on_hashdump_error(self, msg: str):
        self.card_creds.update_value("0")
        self.statusBar().showMessage("⚠  hashdump skipped — continuing pipeline …")
        self._run_auto_yarascan()

    # ── 5. AUTO YARA SCAN ─────────────────────────────────────────────────────
    def _run_auto_yarascan(self):
        """Launch automated YARA scan with Neo23x0 + local rules."""
        self.btn_load.setEnabled(False)
        self.progress.setRange(0, 0)
        self.progress.setVisible(True)
        self.statusBar().showMessage(
            "⏳  [5/5] YARA Signature Scan (Neo23x0 rules) …"
        )

        self._yara_worker = YaraWorker(self.loaded_dump_path)
        self._yara_worker.finished.connect(self._on_yarascan_done)
        self._yara_worker.error.connect(self._on_yarascan_error)
        self._yara_worker.start()

    def _on_yarascan_done(self, rows: list):
        """Append YARA matches to the Malware table after malfind rows."""
        self._finish_pipeline()

        # Build 7-col rows: [PID, Process, Start VPN, End VPN, Protection, Hexdump, Disasm]
        existing = self.page_malware.table.rowCount()
        self.page_malware.table.setRowCount(existing + len(rows))
        for ri, r in enumerate(rows):
            # r = [Rule, PID, Process, Offset, Match]
            yara_row = [
                r[1],                     # PID
                f"[YARA] {r[2]}",         # Process (prefixed)
                r[3],                     # Offset as Start VPN
                "",                       # End VPN
                f"Rule: {r[0]}",          # Protection col → rule name
                r[4],                     # Hexdump col → match string
                "",                       # Disasm
            ]
            for ci, cell in enumerate(yara_row):
                item = QTableWidgetItem(str(cell))
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.page_malware.table.setItem(existing + ri, ci, item)

        total = existing + len(rows)
        self.card_malware.update_value(str(total))
        self.statusBar().showMessage(
            f"✅  All 5 scans complete — {len(self._malfind_rows)} injections + "
            f"{len(rows)} YARA matches = {total} total hits"
        )

    def _on_yarascan_error(self, msg: str):
        self._finish_pipeline()
        self.statusBar().showMessage(
            "✅  Pipeline complete (YARA scan skipped — see status for details)"
        )
