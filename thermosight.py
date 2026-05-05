import os, sys, webbrowser
os.environ['QT_API']            = 'pyqt5'
os.environ['QT_OPENGL']         = 'software'
os.environ['PYVISTA_USE_PANEL'] = '0'
os.environ['PYVISTA_OFF_SCREEN']= 'false'
os.environ['VTK_USE_OFFSCREEN'] = '0'

import vtk
vtk.vtkObject.GlobalWarningDisplayOff()

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QGroupBox, QComboBox,
    QFileDialog, QSplitter, QTextEdit, QProgressBar,
    QSlider, QFrame, QSizePolicy, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor, QColor

try:
    import pyvista as pv
    from pyvistaqt import QtInteractor
    PYVISTA_AVAILABLE = True
except ImportError:
    PYVISTA_AVAILABLE = False

try:
    from pyNastran.bdf.bdf import read_bdf
    NASTRAN_AVAILABLE = True
except ImportError:
    NASTRAN_AVAILABLE = False

try:
    import plotly.graph_objs as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# ─────────────────────────────────────────────────────────────────────────────
#  THEME  —  Left: pastel blue  |  Right: white viewport  |  Gold buttons
# ─────────────────────────────────────────────────────────────────────────────

# Left panel
LEFT_BG      = "#ffffff"
LEFT_PANEL   = "#ffffff"
LEFT_WIDGET  = "#ffffff"
LEFT_BORDER  = "#c8c8c8"

# Right panel
RIGHT_BG     = "#e6e8eb"
BOTTOM_BAR   = "#e6e8eb"
BOT_BORDER   = "#1a2030"

# Text
TEXT_PRI     = "#1a1a1a"
TEXT_SEC     = "#5a5a5a"
TEXT_WHITE   = "#000000"   # buttons now black text

# Gold accent
GOLD         = "#d4a017"
GOLD_LT      = "#e6b800"
GOLD_DARK    = "#a67c00"

# Semantic
SUCCESS      = "#1a7a3a"
ACCENT_HOT   = "#c03020"
ACCENT_ICE   = "#1a6aaa"

# Borders
FRAME_DARK   = "#2a2a2a"
BORDER_MID   = "#aaaaaa"

CMAPS = ['coolwarm', 'RdBu_r', 'jet', 'plasma', 'hot', 'RdYlBu_r'] 
LC_MAX = -9001 
LC_MIN = -9002 
LC_DEFAULT = -9000

STYLE_SHEET = f"""
/* ── Global base ─────────────────────────────────────────────────────────── */
QMainWindow, QWidget {{
    background-color: {LEFT_BG};
    color: {TEXT_PRI};
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
}}

/* ── Right panel (IMPORTANT: assign objectName="rightPanel") ─────────────── */
QWidget#rightPanel {{
    background-color: {RIGHT_BG};
}}

/* ── Bottom bar (optional if used) ───────────────────────────────────────── */
QWidget#bottomBar {{
    background-color: {BOTTOM_BAR};
    border-top: 1px solid {BOT_BORDER};
}}

/* ── Group boxes ─────────────────────────────────────────────────────────── */
QGroupBox {{
    background-color: {LEFT_PANEL};
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    margin-top: 14px;
    padding: 8px 6px 6px 6px;
    font-weight: bold;
    font-size: 10px;
    color: #333333;
    letter-spacing: 1px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    left: 10px;
}}

/* ── Buttons ─────────────────────────────────────────────────────────────── */
QPushButton {{
    background-color: {GOLD};
    color: #000000;
    border: 1px solid {FRAME_DARK};
    border-radius: 4px;
    padding: 5px 12px;
    font-family: 'Consolas', monospace;
    font-size: 11px;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: {GOLD_LT};
    border: 1px solid {GOLD};
}}

QPushButton:pressed {{
    background-color: {GOLD_DARK};
    border: 1px solid {FRAME_DARK};
}}

QPushButton:checked {{
    background-color: {GOLD_DARK};
    border-color: {FRAME_DARK};
    color: #000000;
}}

/* Special buttons */
QPushButton#btn_export {{
    background-color: #2e8b57;
    color: #000000;
    border-color: #1f5e3c;
}}

QPushButton#btn_export:hover {{
    background-color: #3aa76a;
}}

QPushButton#btn_html {{
    background-color: {ACCENT_ICE};
    color: #000000;
    border-color: #124e80;
}}

QPushButton#btn_html:hover {{
    background-color: #2d8cd6;
}}

QPushButton#btn_display {{
    background-color: {GOLD};
    color: #000000;
    border: 1px solid {GOLD_DARK};
    padding: 5px 18px;
    border-radius: 4px;
    letter-spacing: 1px;
}}

QPushButton#btn_display:hover {{
    background-color: {GOLD_LT};   /* lighter gold */
    border: 1px solid {GOLD};      /* highlight border */
}}

QPushButton#btn_minmax {{
    background-color: #d9c27a;
    color: #000000;
    border: 1px solid #a67c00;
    padding: 4px 8px;
}}

QPushButton#btn_minmax:hover {{
    background-color: #e6cf85;
}}

QPushButton#btn_minmax:checked {{
    background-color: #c9b067;
    border-color: #a67c00;
}}

QPushButton#btn_browse {{
    background-color: {GOLD};
    color: #000000;
    border: 1px solid {GOLD_DARK};
    padding: 4px 8px;
    min-width: 58px;
}}

/* ── Inputs / combos ─────────────────────────────────────────────────────── */
QLineEdit, QComboBox {{
    background-color: {LEFT_WIDGET};
    color: #000000;
    border: 1px solid {LEFT_BORDER};
    border-radius: 4px;
    padding: 4px 7px;
    font-family: 'Consolas', monospace;
    font-size: 11px;
}}

QLineEdit:focus, QComboBox:focus {{
    border: 2px solid {GOLD};
}}

QComboBox:hover {{
    border-color: {GOLD};
}}

QComboBox::drop-down {{
    border: none;
    width: 18px;
}}

QComboBox QAbstractItemView {{
    background-color: #ffffff;
    color: #000000;
    border: 1px solid {FRAME_DARK};
    selection-background-color: {GOLD};
    selection-color: #000000;
}}

/* ── Log area (FIXED) ───────────────────────────────────────────────────── */
QTextEdit {{
    background-color: #ffffff;
    color: #1a1a1a;
    border: none;
    font-family: 'Consolas', monospace;
    font-size: 11px;
}}

/* ── Progress bar ───────────────────────────────────────────────────────── */
QProgressBar {{
    background-color: #dcdcdc;
    border: 1px solid {FRAME_DARK};
    border-radius: 4px;
    height: 12px;
    text-align: center;
    font-size: 10px;
    color: #000000;
}}

QProgressBar::chunk {{
    background-color: {GOLD};
    border-radius: 3px;
}}

/* ── Slider ─────────────────────────────────────────────────────────────── */
QSlider::groove:horizontal {{
    background: #d0d0d0;
    border: 1px solid {BORDER_MID};
    height: 4px;
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    background: {GOLD};
    border: 1px solid {GOLD_DARK};
    width: 12px;
    height: 12px;
    margin: -4px 0;
    border-radius: 6px;
}}

QSlider::sub-page:horizontal {{
    background: {GOLD_LT};
    border-radius: 2px;
}}

/* ── Splitter / labels ──────────────────────────────────────────────────── */
QSplitter::handle {{
    background-color: {FRAME_DARK};
    width: 3px;
}}

QLabel {{
    color: {TEXT_SEC};
    font-size: 11px;
}}
"""


# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _parse_pid_filter(text: str):
    text = text.strip()
    if not text or text.lower() == 'all':
        return None
    pids = set()
    for part in text.split(','):
        part = part.strip()
        if '-' in part:
            lo, hi = part.split('-', 1)
            try:
                pids.update(range(int(lo.strip()), int(hi.strip()) + 1))
            except ValueError:
                pass
        else:
            try:
                pids.add(int(part))
            except ValueError:
                pass
    return pids if pids else None


def _try_float(text, default=None):
    try:
        return float(text.strip())
    except (ValueError, AttributeError):
        return default


def _parse_thermal_bdf(filepath, log_fn=None):
    """
    Parse a .bdf file looking for TEMP cards.
    Returns a list of dicts: {loadcase_id, node_id, t}

    TEMP card fixed-field format (8-char fields):
      Field 1 [0:8]   : "TEMP    "
      Field 2 [8:16]  : SID (load-set/thermal-case ID)
      Field 3 [16:24] : G1 (node id)
      Field 4 [24:32] : T1 (temperature)
      Field 5 [32:40] : G2
      Field 6 [40:48] : T2
      Field 7 [48:56] : G3
      Field 8 [56:64] : T3

    One TEMP card can hold up to 3 node–temperature pairs.
    """
    records = []
    try:
        with open(filepath, 'r', errors='replace') as fh:
            for raw in fh:
                line = raw.rstrip('\n')
                # Only process lines that start with TEMP (ignore TEMPD, etc.)
                tag = line[:8].strip().upper()
                if tag != 'TEMP':
                    continue
                try:
                    sid_str = line[8:16].strip()
                    if not sid_str:
                        continue
                    lc_id = int(float(sid_str))
                except (ValueError, IndexError):
                    continue

                # Up to 3 node/temp pairs per TEMP card
                pairs = [
                    (line[16:24], line[24:32]),
                    (line[32:40], line[40:48]),
                    (line[48:56], line[56:64]),
                ]
                for gstr, tstr in pairs:
                    gstr = gstr.strip()
                    tstr = tstr.strip()
                    if not gstr or not tstr:
                        continue
                    try:
                        nid = int(float(gstr))
                        t   = float(tstr)
                        records.append({'loadcase_id': lc_id,
                                        'node_id':     nid,
                                        't':           t})
                    except ValueError:
                        continue
    except Exception as e:
        if log_fn:
            log_fn(f"[WARN]  Could not read {os.path.basename(filepath)}: {e}")
    return records


# ─────────────────────────────────────────────────────────────────────────────
#  WORKER THREADS
# ─────────────────────────────────────────────────────────────────────────────
class BdfLoaderThread(QThread):
    """Loads only the structural BDF — used for gray mesh preview."""
    progress = pyqtSignal(int)
    log      = pyqtSignal(str)
    finished = pyqtSignal(object)
    error    = pyqtSignal(str)

    def __init__(self, bdf_path):
        super().__init__()
        self.bdf_path = bdf_path

    def run(self):
        try:
            self.log.emit(f"[BDF]  Reading: {self.bdf_path}")
            bdf = read_bdf(self.bdf_path, debug=False)
            self.progress.emit(80)
            self.log.emit(f"[BDF]  {len(bdf.nodes)} nodes, {len(bdf.elements)} elements.")
            self.progress.emit(100)
            self.finished.emit(bdf)
        except Exception as e:
            self.error.emit(str(e))


class DataLoaderThread(QThread):
    """
    Loads structural BDF + scans ALL .bdf files in thermal_folder for TEMP cards.
    No filename filtering — any .bdf that contains TEMP cards is used.
    Thermal case ID is read from SID field [8:16] of each TEMP card.
    """
    progress = pyqtSignal(int)
    log      = pyqtSignal(str)
    finished = pyqtSignal(object, object)
    error    = pyqtSignal(str)

    def __init__(self, bdf_path, thermal_folder):
        super().__init__()
        self.bdf_path       = bdf_path
        self.thermal_folder = thermal_folder

    def run(self):
        try:
            self.log.emit(f"[BDF]  Reading: {self.bdf_path}")
            bdf = read_bdf(self.bdf_path, debug=False)
            self.progress.emit(20)

            node_data = np.array(
                [(nid, *node.xyz) for nid, node in bdf.nodes.items()], dtype=float
            )
            node_df = pd.DataFrame(node_data, columns=['node_id','x','y','z'])
            node_df['node_id'] = node_df['node_id'].astype(int)
            self.log.emit(f"[BDF]  {len(node_df)} nodes, {len(bdf.elements)} elements.")
            self.progress.emit(35)

            # Scan ALL .bdf files in the thermal folder
            all_bdf_files = [
                f for f in os.listdir(self.thermal_folder)
                if f.lower().endswith(".bdf")
            ]
            if not all_bdf_files:
                self.error.emit("No .bdf files found in the thermal folder.")
                return

            self.log.emit(f"[SCAN]  {len(all_bdf_files)} .bdf file(s) found — scanning for TEMP cards…")

            all_records = []
            step = 50 // max(len(all_bdf_files), 1)

            for i, fname in enumerate(all_bdf_files):
                filepath = os.path.join(self.thermal_folder, fname)
                recs = _parse_thermal_bdf(
                    filepath,
                    log_fn=lambda msg: self.log.emit(msg)
                )
                if recs:
                    lc_ids = sorted({r['loadcase_id'] for r in recs})
                    self.log.emit(
                        f"[FILE]  {fname}  →  {len(recs)} TEMP records, "
                        f"LC(s): {lc_ids}"
                    )
                    all_records.extend(recs)
                else:
                    self.log.emit(f"[FILE]  {fname}  →  (no TEMP cards)")
                self.progress.emit(35 + (i + 1) * step)

            if not all_records:
                self.error.emit(
                    "No TEMP cards found in any .bdf file in the selected folder.")
                return

            thermal_df = pd.DataFrame(all_records)
            thermal_df['node_id']     = thermal_df['node_id'].astype(int)
            thermal_df['loadcase_id'] = thermal_df['loadcase_id'].astype(int)
            thermal_df['t']           = thermal_df['t'].astype(float)

            # Merge with node coordinates
            thermal_data_full = node_df.merge(thermal_df, on='node_id')
            self.progress.emit(95)
            self.log.emit(
                f"[MERGE]  {len(thermal_data_full)} total rows, "
                f"{thermal_data_full['loadcase_id'].nunique()} unique load case(s)."
            )
            self.progress.emit(100)
            self.finished.emit(thermal_data_full, bdf)

        except Exception as e:
            self.error.emit(str(e))


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────────────────────────────────────
class ThermalViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thermal Viewer  //  FEA Post-Processor")
        self.resize(1520, 900)
        self.thermal_data    = None
        self.bdf             = None
        self._current_df     = None
        self._mesh_actor     = None
        self._current_cmap   = 'coolwarm'
        self._label_actors   = []
        self._minmax_visible = False
        self._env_lc_per_node_max = {}
        self._env_lc_per_node_min = {}
        self._build_ui()
        self.setStyleSheet(STYLE_SHEET)

    # ── BUILD UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(3)
        root.addWidget(splitter, stretch=1)

        splitter.addWidget(self._build_left())
        splitter.addWidget(self._build_right())
        splitter.setSizes([330, 1190])

    # ── LEFT PANEL ────────────────────────────────────────────────────────────
    def _build_left(self):
        panel = QWidget()
        panel.setFixedWidth(330)
        panel.setStyleSheet(f"QWidget {{ background-color: {LEFT_BG}; }}")
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(10)

        # ── File Input ──────────────────────────────────────────────────────
        file_group = QGroupBox("FILE INPUT")
        fv = QVBoxLayout(file_group); fv.setSpacing(6)

        for attr, label, placeholder, slot in [
            ('bdf_edit',  "Structural BDF",  "Select .bdf file…", self._browse_bdf),
            ('thm_edit',  "Thermal Folder",  "Select folder…",    self._browse_thermal_folder),
        ]:
            lbl = QLabel(label)
            lbl.setStyleSheet(f"background:transparent; border:none; color:{TEXT_SEC};")
            fv.addWidget(lbl)
            row = QHBoxLayout()
            edit = QLineEdit(); edit.setPlaceholderText(placeholder)
            btn  = QPushButton("Browse"); btn.setObjectName("btn_browse")
            btn.clicked.connect(slot)
            row.addWidget(edit); row.addWidget(btn)
            fv.addLayout(row)
            setattr(self, attr, edit)

        lay.addWidget(file_group)

        # ── Property Filter ─────────────────────────────────────────────────
        prop_group = QGroupBox("PROPERTY FILTER")
        pv_lay = QVBoxLayout(prop_group); pv_lay.setSpacing(6)
        pid_lbl = QLabel("Property IDs:")
        pid_lbl.setStyleSheet(f"background:transparent; border:none; color:{TEXT_SEC};")
        pv_lay.addWidget(pid_lbl)
        self.prop_input = QLineEdit("All")
        self.prop_input.setPlaceholderText("All  |  1,2,3  |  10-20")
        self.prop_input.returnPressed.connect(self._re_render)
        pv_lay.addWidget(self.prop_input)
        lay.addWidget(prop_group)

        # ── Export buttons ──────────────────────────────────────────────────
        br = QHBoxLayout(); br.setSpacing(8)
        self.export_btn = QPushButton("↓  Excel")
        self.export_btn.setObjectName("btn_export")
        self.export_btn.clicked.connect(self._export_excel)
        self.export_btn.setEnabled(False)
        self.html_btn = QPushButton("⬡  HTML")
        self.html_btn.setObjectName("btn_html")
        self.html_btn.clicked.connect(self._export_html)
        self.html_btn.setEnabled(False)
        br.addWidget(self.export_btn); br.addWidget(self.html_btn)
        lay.addLayout(br)

        # ── Progress ────────────────────────────────────────────────────────
        prog_lbl = QLabel("Progress")
        prog_lbl.setStyleSheet(f"color:{TEXT_SEC}; background:transparent; border:none;")
        lay.addWidget(prog_lbl)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0); self.progress_bar.setFormat("%p%")
        lay.addWidget(self.progress_bar)

        # ── Log window ──────────────────────────────────────────────────────
        lay.addSpacing(12)
        log_frame = QFrame()
        log_frame.setFrameShape(QFrame.StyledPanel)
        log_inner = QVBoxLayout(log_frame)
        log_inner.setContentsMargins(4, 4, 4, 4)
        log_inner.setSpacing(0)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_inner.addWidget(self.log_text)
        lay.addWidget(log_frame, stretch=1)

        return panel

    # ── RIGHT PANEL ───────────────────────────────────────────────────────────
    def _build_right(self):
        panel = QWidget()
        panel.setStyleSheet(f"QWidget {{ background-color: {RIGHT_BG}; }}")
        lay   = QVBoxLayout(panel)
        lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(0)

        if PYVISTA_AVAILABLE:
            try:
                self.plotter = QtInteractor(panel)
                self.plotter.set_background(RIGHT_BG)
                self.plotter.add_axes(color="#444444", viewport=(0.0, 0.0, 0.12, 0.16))
                self.plotter.track_click_position(self._on_pick, side='right')
                lay.addWidget(self.plotter.interactor, stretch=1)
            except Exception as e:
                self.plotter = None
                lay.addWidget(QLabel(f"Viewport error: {e}"), stretch=1)
        else:
            self.plotter = None
            lbl = QLabel("PyVista not installed\npip install pyvista pyvistaqt")
            lbl.setAlignment(Qt.AlignCenter)
            lay.addWidget(lbl, stretch=1)

        lay.addWidget(self._build_bottom_bar())
        return panel

    def _build_bottom_bar(self):
        bar = QFrame()
        bar.setFixedHeight(48)
        bar.setStyleSheet(
            f"QFrame {{ background-color:{BOTTOM_BAR}; border-top:2px solid {FRAME_DARK}; }}"
        )
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(10, 4, 10, 4); bl.setSpacing(6)

        def vsep():
            f = QFrame(); f.setFrameShape(QFrame.VLine)
            f.setStyleSheet(f"color:{BORDER_MID};"); f.setFixedWidth(1)
            return f

        def bare_lbl(text):
            l = QLabel(text)
            l.setStyleSheet(
                f"color:{TEXT_SEC}; font-size:11px; background:transparent; border:none;"
            )
            return l

        bl.addWidget(bare_lbl("Case:"))
        self.case_combo = QComboBox()
        self.case_combo.addItem("-- load first --")
        self.case_combo.setMinimumWidth(130)
        bl.addWidget(self.case_combo)

        self.display_btn = QPushButton("Display")
        self.display_btn.setObjectName("btn_display")
        self.display_btn.clicked.connect(self._display_case)
        self.display_btn.setEnabled(False)
        self.display_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {GOLD};
                color: black;
                border: 1px solid {GOLD_DARK};
                border-radius: 4px;
                padding: 5px 18px;
            }}
        """)
        bl.addWidget(self.display_btn)
    
        bl.addWidget(vsep())

        bl.addWidget(bare_lbl("Cmap:"))
        self.cmap_combo = QComboBox()
        for cm in CMAPS: self.cmap_combo.addItem(cm)
        self.cmap_combo.setCurrentText('coolwarm')
        self.cmap_combo.setMinimumWidth(100)
        self.cmap_combo.currentTextChanged.connect(self._on_cmap_changed)
        bl.addWidget(self.cmap_combo)

        bl.addWidget(vsep())

        bl.addWidget(bare_lbl("T min:"))
        self.thresh_min_edit = QLineEdit()
        self.thresh_min_edit.setPlaceholderText("auto")
        self.thresh_min_edit.setFixedWidth(58)
        self.thresh_min_edit.returnPressed.connect(self._re_render)
        bl.addWidget(self.thresh_min_edit)

        bl.addWidget(bare_lbl("T max:"))
        self.thresh_max_edit = QLineEdit()
        self.thresh_max_edit.setPlaceholderText("auto")
        self.thresh_max_edit.setFixedWidth(58)
        self.thresh_max_edit.returnPressed.connect(self._re_render)
        bl.addWidget(self.thresh_max_edit)

        bl.addWidget(vsep())

        self.minmax_btn = QPushButton("⊕ Min/Max")
        self.minmax_btn.setObjectName("btn_minmax")
        self.minmax_btn.setCheckable(True)
        self.minmax_btn.setToolTip("Highlight global min & max nodes with labels")
        self.minmax_btn.clicked.connect(self._toggle_minmax_labels)
        bl.addWidget(self.minmax_btn)

        bl.addWidget(vsep())

        self.edges_btn = QPushButton("🧱")
        self.edges_btn.setCheckable(True); self.edges_btn.setChecked(True)
        self.edges_btn.setFixedWidth(34); self.edges_btn.setToolTip("Toggle interior edges")
        self.edges_btn.clicked.connect(self._toggle_edges)
        bl.addWidget(self.edges_btn)

        bl.addWidget(vsep())

        for label, tip, mode in [("XY","Top","xy"),("YZ","Front","yz"),
                                   ("XZ","Side","xz"),("R","Iso","iso")]:
            b = QPushButton(label); b.setFixedWidth(30); b.setToolTip(tip)
            b.clicked.connect(self._make_view_fn(mode))
            bl.addWidget(b)

        bl.addWidget(vsep())

        bl.addWidget(bare_lbl("Opacity:"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(10, 100); self.opacity_slider.setValue(100)
        self.opacity_slider.setFixedWidth(70)
        self.opacity_slider.valueChanged.connect(self._on_opacity_changed)
        bl.addWidget(self.opacity_slider)
        self.opacity_lbl = QLabel("100%")
        self.opacity_lbl.setFixedWidth(34)
        self.opacity_lbl.setStyleSheet(
            f"color:{TEXT_PRI}; font-size:11px; background:transparent; border:none;"
        )
        bl.addWidget(self.opacity_lbl)

        bl.addWidget(vsep())

        self.status_label = QLabel("Right-click a node to inspect")
        self.status_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.status_label.setStyleSheet(f"""
            color:{ACCENT_ICE}; font-family:'Consolas',monospace; font-size:11px;
            background:transparent; border:none; padding-right:4px;
            font-weight: bold;
        """)
        bl.addWidget(self.status_label, stretch=1)

        return bar

    def _make_view_fn(self, mode):
        def fn():
            if not self.plotter: return
            {"xy":self.plotter.view_xy,"yz":self.plotter.view_yz,
             "xz":self.plotter.view_xz,"iso":self.plotter.view_isometric}[mode]()
            self.plotter.render()
        return fn

    # ── BROWSE / AUTO-LOAD ────────────────────────────────────────────────────
    def _browse_bdf(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Structural BDF", "", "BDF Files (*.bdf *.BDF);;All (*)")
        if path:
            self.bdf_edit.setText(path)
            self._auto_load_if_ready()

    def _browse_thermal_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Thermal Folder")
        if folder:
            self.thm_edit.setText(folder)
            self._auto_load_if_ready()

    def _auto_load_if_ready(self):
        bdf_ok = os.path.isfile(self.bdf_edit.text().strip())
        thm_ok = os.path.isdir(self.thm_edit.text().strip())

        if bdf_ok and thm_ok:
            self._load_data()
        elif bdf_ok and not thm_ok:
            self._load_bdf_only()

    # ── BDF-ONLY GRAY MESH PREVIEW ────────────────────────────────────────────
    def _load_bdf_only(self):
        self.progress_bar.setValue(0)
        self.log_text.clear()
        self._log("[START]  Loading BDF for structural preview…")
        self._bdf_worker = BdfLoaderThread(self.bdf_edit.text().strip())
        self._bdf_worker.progress.connect(self.progress_bar.setValue)
        self._bdf_worker.log.connect(self._log)
        self._bdf_worker.finished.connect(self._on_bdf_only_loaded)
        self._bdf_worker.error.connect(self._on_load_error)
        self._bdf_worker.start()

    def _on_bdf_only_loaded(self, bdf):
        self.bdf = bdf
        self._log("[DONE]  BDF loaded — gray mesh preview active. Select thermal folder to load results.")
        self.case_combo.clear()
        self.case_combo.addItem("Default View", userData=LC_DEFAULT)
        self.display_btn.setEnabled(True)
        self._display_default_mesh()

    def _display_default_mesh(self):
        if self.bdf is None or not self.plotter:
            return

        self._log("[VIZ]  Structural mesh preview…")
        self._label_actors.clear()
        self._minmax_visible = False
        self.minmax_btn.setChecked(False)
        self.plotter.clear()

        node_xyz = {nid: node.xyz for nid, node in self.bdf.nodes.items()}
        nid_list = sorted(node_xyz.keys())
        nmap     = {nid: i for i, nid in enumerate(nid_list)}
        pts      = np.array([node_xyz[nid] for nid in nid_list], dtype=float)

        pid_filter = _parse_pid_filter(self.prop_input.text())
        sh_cells, bar_pts2, bar_lines = [], [], []

        for eid, elem in self.bdf.elements.items():
            try:
                if pid_filter is not None and elem.pid not in pid_filter:
                    continue
                if elem.type in ('CQUAD4','CQUAD8','CQUAD'):
                    nids = elem.node_ids[:4]
                    if all(n in nmap for n in nids):
                        sh_cells.append([4] + [nmap[n] for n in nids])
                elif elem.type in ('CTRIA3','CTRIA6'):
                    nids = elem.node_ids[:3]
                    if all(n in nmap for n in nids):
                        sh_cells.append([3] + [nmap[n] for n in nids])
                elif elem.type in ('CBAR','CBEAM','CROD'):
                    nids = elem.node_ids[:2]
                    if all(n in nmap for n in nids):
                        i = len(bar_pts2)
                        bar_pts2.append(pts[nmap[nids[0]]])
                        bar_pts2.append(pts[nmap[nids[1]]])
                        bar_lines.append([2, i, i+1])
            except Exception:
                continue

        GRAY_MESH = "#7a8aa0"
        GRAY_EDGE = "#3a5070"
        show_edges = self.edges_btn.isChecked()
        op         = self.opacity_slider.value() / 100.0

        if sh_cells:
            mesh = pv.PolyData(pts, np.hstack(sh_cells))
            self._mesh_actor = self.plotter.add_mesh(
                mesh, color=GRAY_MESH,
                show_edges=show_edges, edge_color=GRAY_EDGE, line_width=0.5,
                opacity=op, pickable=True,
            )
            boundary = mesh.extract_feature_edges(
                boundary_edges=True, non_manifold_edges=False,
                feature_edges=False, manifold_edges=False)
            if boundary.n_points > 0:
                self.plotter.add_mesh(boundary, color="#2a4a6a",
                                      line_width=1.5, pickable=False)
            self._log(f"[VIZ]  {len(sh_cells)} shell faces (structural preview).")
        else:
            self._log("[VIZ]  No shell elements — point cloud fallback.")
            cloud = pv.PolyData(pts)
            self._mesh_actor = self.plotter.add_mesh(
                cloud, color=GRAY_MESH, point_size=7,
                render_points_as_spheres=True, opacity=op, pickable=True,
            )

        if bar_lines:
            bm = pv.PolyData(np.array(bar_pts2), lines=np.hstack(bar_lines))
            self.plotter.add_mesh(bm, color=GRAY_MESH, line_width=5,
                                  render_lines_as_tubes=True, opacity=op)
            self._log(f"[VIZ]  {len(bar_lines)} bar elements.")

        self.plotter.add_axes(color='#444444', viewport=(0.0, 0.0, 0.12, 0.16))
        self.plotter.reset_camera()
        self._current_df = None
        self.status_label.setText("Structural mesh preview — load thermal folder for results")

    # ── FULL DATA LOADING ─────────────────────────────────────────────────────
    def _load_data(self):
        self.export_btn.setEnabled(False); self.html_btn.setEnabled(False)
        self.display_btn.setEnabled(False)
        self.progress_bar.setValue(0); self.log_text.clear()
        self._log("[START]  Loading…")

        self._worker = DataLoaderThread(
            self.bdf_edit.text().strip(), self.thm_edit.text().strip())
        self._worker.progress.connect(self.progress_bar.setValue)
        self._worker.log.connect(self._log)
        self._worker.finished.connect(self._on_data_loaded)
        self._worker.error.connect(self._on_load_error)
        self._worker.start()

    def _on_data_loaded(self, df, bdf):
        self.thermal_data = df[['node_id','loadcase_id','x','y','z','t']]
        self.bdf          = bdf
        self._log(f"[DONE]  {len(df)} rows ready.")

        xyz = df[['node_id','x','y','z']].drop_duplicates('node_id')

        self._env_lc_per_node_max = {}
        self._env_lc_per_node_min = {}
        for nid, grp in df.groupby('node_id'):
            self._env_lc_per_node_max[int(nid)] = int(
                grp.loc[grp['t'].idxmax(), 'loadcase_id'])
            self._env_lc_per_node_min[int(nid)] = int(
                grp.loc[grp['t'].idxmin(), 'loadcase_id'])

        for lc_id, agg_fn in [(LC_MAX, 'max'), (LC_MIN, 'min')]:
            agg   = df.groupby('node_id')['t'].agg(agg_fn).reset_index()
            synth = agg.copy()
            synth['loadcase_id'] = lc_id
            synth = synth.merge(xyz, on='node_id')[['node_id','loadcase_id','x','y','z','t']]
            self.thermal_data = pd.concat([self.thermal_data, synth], ignore_index=True)
        self._log("[SYNTH]  MAX and MIN envelope load cases added.")

        real_cases = sorted(df['loadcase_id'].unique().tolist())

        self.case_combo.clear()
        self.case_combo.addItem("Default View", userData=LC_DEFAULT)
        for c in real_cases:
            self.case_combo.addItem(str(int(c)), userData=int(c))
        self.case_combo.addItem("MAX (envelope)", userData=LC_MAX)
        self.case_combo.addItem("MIN (envelope)", userData=LC_MIN)

        self.export_btn.setEnabled(True); self.html_btn.setEnabled(True)
        self.display_btn.setEnabled(True)

        self.case_combo.setCurrentIndex(1)
        self._display_case()

    def _on_load_error(self, msg):
        self._log(f"[ERROR]  {msg}")
        QMessageBox.critical(self, "Load Error", msg)

    # ── VISUALIZATION HELPERS ─────────────────────────────────────────────────
    def _get_display_df(self):
        lc = self.case_combo.currentData()
        if lc == LC_DEFAULT:
            return None
        return (self.thermal_data[self.thermal_data['loadcase_id'] == lc]
                    .copy().reset_index(drop=True))

    def _build_mesh_data(self, df):
        pid_filter = _parse_pid_filter(self.prop_input.text())
        nmap  = {int(r.node_id): i for i, r in df.iterrows()}
        pts   = df[['x','y','z']].values.astype(float)
        temps = df['t'].values.astype(float)
        sh_cells, bar_pts2, bar_lines = [], [], []

        for eid, elem in self.bdf.elements.items():
            try:
                if pid_filter is not None and elem.pid not in pid_filter:
                    continue
                if elem.type in ('CQUAD4','CQUAD8','CQUAD'):
                    nids = elem.node_ids[:4]
                    if all(n in nmap for n in nids):
                        sh_cells.append([4] + [nmap[n] for n in nids])
                elif elem.type in ('CTRIA3','CTRIA6'):
                    nids = elem.node_ids[:3]
                    if all(n in nmap for n in nids):
                        sh_cells.append([3] + [nmap[n] for n in nids])
                elif elem.type in ('CBAR','CBEAM','CROD'):
                    nids = elem.node_ids[:2]
                    if all(n in nmap for n in nids):
                        i = len(bar_pts2)
                        bar_pts2.append(pts[nmap[nids[0]]])
                        bar_pts2.append(pts[nmap[nids[1]]])
                        bar_lines.append([2, i, i+1])
            except Exception:
                continue

        return pts, temps, sh_cells, bar_pts2, bar_lines, nmap

    def _get_clim(self, temps):
        t_lo = _try_float(self.thresh_min_edit.text())
        t_hi = _try_float(self.thresh_max_edit.text())
        lo   = t_lo if t_lo is not None else float(temps.min())
        hi   = t_hi if t_hi is not None else float(temps.max())
        if lo >= hi:
            lo, hi = float(temps.min()), float(temps.max())
        over_color  = 'red'  if t_hi is not None else None
        under_color = 'blue' if t_lo is not None else None
        return lo, hi, over_color, under_color

    # ── DISPLAY CASE ─────────────────────────────────────────────────────────
    def _display_case(self):
        if self.bdf is None:
            return

        lc = self.case_combo.currentData()

        if lc == LC_DEFAULT:
            self._display_default_mesh()
            return

        if self.thermal_data is None:
            return

        lc_label = self.case_combo.currentText()
        df = self._get_display_df()
        if df is None or df.empty:
            self._log(f"[WARN]  No data for {lc_label}."); return

        self._log(f"[VIZ]  {lc_label} — {len(df)} nodes…")
        self._label_actors.clear()
        self._minmax_visible = False
        self.minmax_btn.setChecked(False)
        self.plotter.clear()

        pts, temps, sh_cells, bar_pts2, bar_lines, _ = self._build_mesh_data(df)
        cmap  = self._current_cmap
        op    = self.opacity_slider.value() / 100.0
        show_edges = self.edges_btn.isChecked()
        lo, hi, over_col, under_col = self._get_clim(temps)

        # Colorbar with °C unit label
        scalar_bar_args = {
            'title'      : 'Temperature\n(°C)',
            'color'      : '#1a2030',
            'fmt'        : '%.1f°C',
            'vertical'   : True,
            'position_x' : 0.87,
            'position_y' : 0.08,
            'width'      : 0.07,
            'height'     : 0.75,
            'title_font_size' : 12,
            'label_font_size' : 11,
        }

        mesh_kwargs = dict(
            scalars='Temperature', preference='point',
            cmap=cmap, clim=[lo, hi],
            opacity=op, scalar_bar_args=scalar_bar_args,
            pickable=True,
        )
        if over_col:  mesh_kwargs['above_color']  = over_col
        if under_col: mesh_kwargs['below_color'] = under_col

        if sh_cells:
            mesh = pv.PolyData(pts, np.hstack(sh_cells))
            mesh.point_data['Temperature'] = temps
            self._mesh_actor = self.plotter.add_mesh(
                mesh, show_edges=show_edges,
                edge_color="#1a2030", line_width=0.5,
                **mesh_kwargs,
            )
            boundary = mesh.extract_feature_edges(
                boundary_edges=True, non_manifold_edges=False,
                feature_edges=False, manifold_edges=False)
            if boundary.n_points > 0:
                self.plotter.add_mesh(boundary, color="#2a4a6a",
                                      line_width=1.5, pickable=False)
            self._log(f"[VIZ]  {len(sh_cells)} shell faces.")
        else:
            self._log("[VIZ]  No shell elements — point cloud fallback.")
            cloud = pv.PolyData(pts)
            cloud['Temperature'] = temps
            self._mesh_actor = self.plotter.add_mesh(
                cloud, point_size=7, render_points_as_spheres=True,
                **mesh_kwargs)

        if bar_lines:
            bm    = pv.PolyData(np.array(bar_pts2), lines=np.hstack(bar_lines))
            bar_t = np.array([(temps[bar_lines[i][1]] + temps[bar_lines[i][2]]) / 2
                               for i in range(len(bar_lines))])
            bm.cell_data['Temperature'] = bar_t
            bar_kw = dict(scalars='Temperature', cmap=cmap, clim=[lo, hi],
                          line_width=5, render_lines_as_tubes=True,
                          opacity=op, show_scalar_bar=False)
            if over_col:  bar_kw['above_color']  = over_col
            if under_col: bar_kw['below_color'] = under_col
            self.plotter.add_mesh(bm, **bar_kw)
            self._log(f"[VIZ]  {len(bar_lines)} bar elements.")

        self.plotter.add_axes(color='#444444', viewport=(0.0, 0.0, 0.12, 0.16))
        self.plotter.reset_camera()
        self._current_df = df
        self._log(f"[VIZ]  T range: {temps.min():.2f}°C – {temps.max():.2f}°C")

    def _re_render(self):
        lc = self.case_combo.currentData()
        if lc == LC_DEFAULT:
            self._display_default_mesh()
        elif self._current_df is not None:
            self._display_case()

    # ── MIN/MAX HIGHLIGHT ─────────────────────────────────────────────────────
    def _toggle_minmax_labels(self):
        if self._current_df is None or not self.plotter:
            self.minmax_btn.setChecked(False)
            return

        if not self.minmax_btn.isChecked():
            for actor in self._label_actors:
                try:
                    self.plotter.remove_actor(actor)
                except Exception:
                    pass
            self._label_actors.clear()
            self._minmax_visible = False
            self.plotter.render()
            return

        df    = self._current_df
        temps = df['t'].values.astype(float)
        pts   = df[['x','y','z']].values.astype(float)

        idx_max = int(np.argmax(temps))
        idx_min = int(np.argmin(temps))
        lc      = self.case_combo.currentData()

        for idx, color, tag in [
            (idx_max, '#ff3333', 'MAX'),
            (idx_min, '#33aaff', 'MIN'),
        ]:
            nid   = int(df.iloc[idx]['node_id'])
            t_val = float(df.iloc[idx]['t'])
            pos   = pts[idx]

            lc_note = ""
            if lc == LC_MAX and tag == 'MAX':
                src = self._env_lc_per_node_max.get(nid)
                if src is not None:
                    lc_note = f"\nLC {src}"
            elif lc == LC_MIN and tag == 'MIN':
                src = self._env_lc_per_node_min.get(nid)
                if src is not None:
                    lc_note = f"\nLC {src}"

            pt_cloud = pv.PolyData(pos.reshape(1,3))
            actor = self.plotter.add_mesh(
                pt_cloud, color=color,
                point_size=18, render_points_as_spheres=True, pickable=False
            )
            self._label_actors.append(actor)

            label_text = f"{tag}\nNode {nid}\nT={t_val:.2f}°C{lc_note}"
            txt_actor = self.plotter.add_point_labels(
                np.array([pos]), [label_text],
                font_size=11, text_color=color,
                point_color=color, point_size=0,
                bold=True, shape='rounded_rect',
                shape_color='#f0f0f0', shape_opacity=0.88,
                show_points=False, always_visible=True,
            )
            self._label_actors.append(txt_actor)

        self._minmax_visible = True
        self.plotter.render()
        self._log(
            f"[MIN/MAX]  MAX: Node {int(df.iloc[idx_max].node_id)} "
            f"T={float(df.iloc[idx_max].t):.2f}°C  |  "
            f"MIN: Node {int(df.iloc[idx_min].node_id)} "
            f"T={float(df.iloc[idx_min].t):.2f}°C"
        )

    # ── BOTTOM BAR CALLBACKS ──────────────────────────────────────────────────
    def _on_cmap_changed(self, name):
        self._current_cmap = name
        if self._current_df is not None: self._display_case()

    def _toggle_edges(self):
        lc = self.case_combo.currentData()
        if lc == LC_DEFAULT:
            self._display_default_mesh()
        elif self._current_df is not None:
            self._display_case()

    def _on_opacity_changed(self, val):
        self.opacity_lbl.setText(f"{val}%")
        if self._mesh_actor is not None:
            try:
                self._mesh_actor.GetProperty().SetOpacity(val / 100.0)
                self.plotter.render()
            except Exception:
                pass

    # ── PICK / STATUS ─────────────────────────────────────────────────────────
    def _on_pick(self, pos):
        if pos is None:
            return

        lc = self.case_combo.currentData()

        if lc == LC_DEFAULT or self._current_df is None:
            if self.bdf is None:
                return
            node_xyz = {nid: node.xyz for nid, node in self.bdf.nodes.items()}
            nid_list = sorted(node_xyz.keys())
            pts      = np.array([node_xyz[nid] for nid in nid_list], dtype=float)
            dists    = np.linalg.norm(pts - np.array(pos), axis=1)
            idx      = int(np.argmin(dists))
            nid      = nid_list[idx]
            x, y, z  = node_xyz[nid]
            self.status_label.setText(
                f"[Default View]  Node {nid}  ({x:.3f}, {y:.3f}, {z:.3f})"
            )
            return

        pts   = self._current_df[['x','y','z']].values
        dists = np.linalg.norm(pts - np.array(pos), axis=1)
        idx   = int(np.argmin(dists))
        row   = self._current_df.iloc[idx]
        nid   = int(row.node_id)

        if lc == LC_MAX:
            src_lc = self._env_lc_per_node_max.get(nid)
            lc_str = f"LC {src_lc}" if src_lc is not None else "MAX env"
        elif lc == LC_MIN:
            src_lc = self._env_lc_per_node_min.get(nid)
            lc_str = f"LC {src_lc}" if src_lc is not None else "MIN env"
        else:
            lc_str = f"LC {int(lc)}"

        self.status_label.setText(
            f"[{lc_str}]  Node {nid}  "
            f"({float(row.x):.3f}, {float(row.y):.3f}, {float(row.z):.3f})  "
            f"|  T = {float(row.t):.4f} °C"
        )

    # ── EXPORT EXCEL ──────────────────────────────────────────────────────────
    def _export_excel(self):
        if self.thermal_data is None: return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Excel", "thermal_data.xlsx",
            "Excel Files (*.xlsx);;All Files (*)")
        if path:
            try:
                real = self.thermal_data[
                    ~self.thermal_data['loadcase_id'].isin([LC_MAX, LC_MIN, LC_DEFAULT])]
                real[['node_id','loadcase_id','x','y','z','t']].to_excel(path, index=False)
                self._log(f"[EXPORT]  → {path}")
            except Exception as e:
                self._log(f"[ERROR]  {e}")
                QMessageBox.critical(self, "Export Error", str(e))

    # ── EXPORT HTML ───────────────────────────────────────────────────────────
    def _export_html(self):
        if self.thermal_data is None or self.bdf is None: return
        if not PLOTLY_AVAILABLE:
            QMessageBox.warning(self, "Missing Library",
                                "plotly is not installed.\npip install plotly"); return

        lc_id    = self.case_combo.currentData()
        lc_label = self.case_combo.currentText()

        if lc_id == LC_DEFAULT:
            QMessageBox.information(
                self, "No Thermal Data",
                "Switch to a thermal load case before exporting HTML."); return

        df = self._get_display_df()
        if df is None or df.empty:
            QMessageBox.warning(self, "No Data", f"No data for {lc_label}."); return

        path, _ = QFileDialog.getSaveFileName(
            self, "Export HTML",
            f"thermal_{lc_label.replace(' ','_').replace('(','').replace(')','')}.html",
            "HTML Files (*.html);;All Files (*)")
        if not path: return

        try:
            self._log(f"[HTML]  Building plot for {lc_label}…")
            pts, temps, sh_cells, bar_pts2, bar_lines, _ = self._build_mesh_data(df)
            lo, hi, _, _ = self._get_clim(temps)
            node_ids = df['node_id'].values.astype(int)

            cmap_plotly = {
                'coolwarm':'RdBu_r','RdBu_r':'RdBu_r','jet':'Jet',
                'plasma':'Plasma','hot':'Hot','RdYlBu_r':'RdYlBu',
            }.get(self._current_cmap, 'RdBu_r')

            colorbar_cfg = dict(
                title=dict(text='Temperature (°C)',
                           font=dict(size=13, color='#1a2030')),
                tickfont=dict(size=11, color='#1a2030'),
                ticksuffix='°C',
                len=0.75, thickness=16, x=1.0, xpad=8,
                bgcolor='rgba(255,255,255,0)',
                bordercolor='rgba(0,0,0,0)', borderwidth=0,
            )

            traces = []

            if sh_cells:
                i_tri, j_tri, k_tri = [], [], []
                for cell in sh_cells:
                    if cell[0] == 4:
                        a,b,c,d = cell[1],cell[2],cell[3],cell[4]
                        i_tri += [a,a]; j_tri += [b,c]; k_tri += [c,d]
                    else:
                        i_tri.append(cell[1]); j_tri.append(cell[2]); k_tri.append(cell[3])

                temps_clamped = np.clip(temps, lo, hi)

                # Build element edge lines — walk each face, append None separator
                # between elements so one Scatter3d trace draws all edges cleanly.
                edge_x, edge_y, edge_z = [], [], []
                for cell in sh_cells:
                    if cell[0] == 4:
                        verts = [cell[1], cell[2], cell[3], cell[4], cell[1]]  # close quad
                    else:
                        verts = [cell[1], cell[2], cell[3], cell[1]]           # close tri
                    for v in verts:
                        edge_x.append(float(pts[v, 0]))
                        edge_y.append(float(pts[v, 1]))
                        edge_z.append(float(pts[v, 2]))
                    # None separator — breaks the line between elements
                    edge_x.append(None); edge_y.append(None); edge_z.append(None)

                traces.append(go.Mesh3d(
                    x=pts[:,0], y=pts[:,1], z=pts[:,2],
                    i=i_tri, j=j_tri, k=k_tri,
                    intensity=temps_clamped, cmin=lo, cmax=hi,
                    colorscale=cmap_plotly, colorbar=colorbar_cfg,
                    flatshading=False,
                    lighting=dict(ambient=0.65, diffuse=0.85, specular=0.05),
                    lightposition=dict(x=1000, y=2000, z=3000),
                    customdata=np.column_stack([node_ids, temps]),
                    hovertemplate=(
                        '<b>Node %{customdata[0]}</b><br>'
                        'X: %{x:.3f}  Y: %{y:.3f}  Z: %{z:.3f}<br>'
                        'T: %{customdata[1]:.4f} °C<extra></extra>'
                    ),
                    showlegend=False,
                    opacity=self.opacity_slider.value() / 100.0,
                ))

                # Mesh edges overlay
                if edge_x:
                    traces.append(go.Scatter3d(
                        x=edge_x, y=edge_y, z=edge_z,
                        mode='lines',
                        line=dict(color='rgba(0,0,0,0.25)', width=1),
                        hoverinfo='skip',
                        showlegend=False,
                    ))

            if bar_lines:
                bar_pts_arr = np.array(bar_pts2)
                x_seg, y_seg, z_seg = [], [], []
                for bl_item in bar_lines:
                    p1, p2 = bar_pts_arr[bl_item[1]], bar_pts_arr[bl_item[2]]
                    x_seg += [p1[0],p2[0],None]
                    y_seg += [p1[1],p2[1],None]
                    z_seg += [p1[2],p2[2],None]
                traces.append(go.Scatter3d(
                    x=x_seg, y=y_seg, z=z_seg, mode='lines',
                    line=dict(color='#2e8fcf', width=5),
                    hoverinfo='skip', showlegend=False,
                ))

            if not sh_cells and not bar_lines:
                traces.append(go.Scatter3d(
                    x=pts[:,0], y=pts[:,1], z=pts[:,2], mode='markers',
                    marker=dict(size=4, color=np.clip(temps,lo,hi),
                                colorscale=cmap_plotly, cmin=lo, cmax=hi,
                                colorbar=colorbar_cfg, showscale=True),
                    customdata=np.column_stack([node_ids, temps]),
                    hovertemplate=(
                        '<b>Node %{customdata[0]}</b><br>'
                        'X: %{x:.3f}  Y: %{y:.3f}  Z: %{z:.3f}<br>'
                        'T: %{customdata[1]:.4f} °C<extra></extra>'
                    ),
                    showlegend=False,
                ))

            lc_str = lc_label if lc_id in (LC_MAX, LC_MIN) else f"Load Case {int(lc_id)}"
            annotation_text = (
                f"<b>{lc_str}</b><br>"
                f"T min:  {temps.min():.2f} °C<br>"
                f"T max:  {temps.max():.2f} °C"
            )

            layout = go.Layout(
                scene=dict(
                    xaxis=dict(visible=False), yaxis=dict(visible=False),
                    zaxis=dict(visible=False), aspectmode='data',
                    bgcolor='#ffffff',
                ),
                paper_bgcolor='#ffffff', plot_bgcolor='#ffffff',
                font=dict(color='#1e2029', family='Consolas, monospace'),
                margin=dict(l=0, r=0, t=0, b=0),
                showlegend=False,
                annotations=[dict(
                    text=annotation_text,
                    xref='paper', yref='paper',
                    x=0.015, y=0.985,
                    xanchor='left', yanchor='top',
                    showarrow=False,
                    bgcolor='rgba(255,255,255,0.7)',
                    bordercolor='#b0b8cc', borderwidth=1, borderpad=12,
                    font=dict(size=13, color='#1e2029', family='Consolas, monospace'),
                )],
            )

            fig = go.Figure(data=traces, layout=layout)
            fig.update_layout(scene_camera=dict(
                eye=dict(x=1.4, y=1.4, z=1.2),
                center=dict(x=0, y=0, z=0),
                up=dict(x=0, y=0, z=1),
            ))
            fig.write_html(path,
                           config={'displayModeBar':True,'displaylogo':False},
                           include_plotlyjs='cdn')

            self._log(f"[HTML]  → {path}")
            webbrowser.open('file://' + os.path.abspath(path))

        except Exception as e:
            self._log(f"[ERROR]  HTML export failed: {e}")
            QMessageBox.critical(self, "HTML Export Error", str(e))

    # ── HELPERS ───────────────────────────────────────────────────────────────
    def _log(self, msg):
        color_map = {
            '[ERROR]'  : '#c03020',
            '[WARN]'   : '#8a6000',
            '[DONE]'   : '#1a6a38',
            '[HTML]'   : '#1a5aaa',
            '[VIZ]'    : '#1a5aaa',
            '[MIN/MAX]': '#8a6000',
            '[SCAN]'   : '#2a6a9a',
            '[FILE]'   : '#2a7aaa',
            '[SYNTH]'  : '#1a6a38',
            '[MERGE]'  : '#1a6a38',
        }
        color = '#1a4a6a'
        for key, col in color_map.items():
            if key in msg:
                color = col; break
        self.log_text.setTextColor(QColor(color))
        self.log_text.append(msg)
        self.log_text.setTextColor(QColor('#1a4a6a'))
        self.log_text.moveCursor(QTextCursor.End)

    def closeEvent(self, event):
        if PYVISTA_AVAILABLE and self.plotter:
            self.plotter.close()
        event.accept()


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = ThermalViewer()
    win.show()
    sys.exit(app.exec_())
