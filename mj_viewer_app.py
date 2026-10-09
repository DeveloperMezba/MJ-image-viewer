import sys
import os
import struct
import json
import time
import urllib.request
from PIL import Image

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox, QFrame,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QMenu, QDialog
)
from PyQt6.QtGui import QPixmap, QImage, QKeySequence, QShortcut, QAction, QPainter
from PyQt6.QtCore import Qt

# Metadata & GitHub Auto-Update Configuration
CURRENT_VERSION = "v1.0.2"
DEVELOPER_NAME = "Mezba"
GITHUB_REPO_URL = "https://api.github.com/repos/DeveloperMezba/MJ-image-viewer/releases/latest"
RAW_SCRIPT_URL = "https://raw.githubusercontent.com/DeveloperMezba/MJ-image-viewer/main/mj_viewer_app.py"

SECRET_KEY = 0x5A
SUPPORTED_EXTENSIONS = ('.mj', '.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif')

class SmoothGraphicsView(QGraphicsView):
    """
    Custom QGraphicsView with smooth, mouse-centered zooming and grab-hand panning.
    """
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

    def wheelEvent(self, event):
        if not self.scene() or not self.scene().items():
            super().wheelEvent(event)
            return

        zoom_in_factor = 1.12
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
        elif event.angleDelta().y() < 0:
            self.scale(zoom_out_factor, zoom_out_factor)


class MJApp(QMainWindow):
    def __init__(self, initial_file=None):
        super().__init__()
        self.current_file_path = None
        self.folder_files = []
        self.current_index = -1
        self.image_info = {}
        self.loaded_pil_image = None
        self.current_rotation = 0

        self.init_ui()

        if initial_file and os.path.exists(initial_file):
            self.load_file(initial_file)

    def init_ui(self):
        self.setWindowTitle("MJ Image Viewer")
        self.resize(1050, 720)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e2e; }
            QFrame#topBar { background-color: #2b2b3b; border-bottom: 1px solid #3b3b4b; }
            QPushButton {
                background-color: #3b4252;
                color: #eceff4;
                border: 1px solid #4c566a;
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #434c5e; }
            QPushButton:pressed { background-color: #5e81ac; }
            QPushButton:disabled { background-color: #2e3440; color: #4c566a; border-color: #3b3b4b; }
            QMenu {
                background-color: #2b2b3b;
                color: #eceff4;
                border: 1px solid #4c566a;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 25px 8px 15px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #5e81ac;
                color: #ffffff;
            }
            QLabel { color: #d8dee9; }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top Bar
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(10, 8, 10, 8)
        top_layout.setSpacing(8)

        self.btn_prev = QPushButton("◀ Prev")
        self.btn_prev.setToolTip("Previous image (Left Arrow)")
        self.btn_prev.clicked.connect(self.show_prev_image)
        self.btn_prev.setEnabled(False)
        top_layout.addWidget(self.btn_prev)

        self.btn_next = QPushButton("Next ▶")
        self.btn_next.setToolTip("Next image (Right Arrow)")
        self.btn_next.clicked.connect(self.show_next_image)
        self.btn_next.setEnabled(False)
        top_layout.addWidget(self.btn_next)

        top_layout.addStretch()

        self.lbl_status = QLabel("No image loaded")
        self.lbl_status.setStyleSheet("color: #888c96; font-size: 13px; font-weight: bold;")
        top_layout.addWidget(self.lbl_status)

        top_layout.addStretch()

        self.btn_rotate = QPushButton("🔄 Rotate")
        self.btn_rotate.setToolTip("Rotate view 90° Right (Shortcut: R)")
        self.btn_rotate.clicked.connect(self.rotate_image)
        self.btn_rotate.setEnabled(False)
        top_layout.addWidget(self.btn_rotate)

        self.btn_zoom_in = QPushButton("➕ Zoom In")
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        self.btn_zoom_in.setEnabled(False)
        top_layout.addWidget(self.btn_zoom_in)

        self.btn_zoom_out = QPushButton("➖ Zoom Out")
        self.btn_zoom_out.clicked.connect(self.zoom_out)
        self.btn_zoom_out.setEnabled(False)
        top_layout.addWidget(self.btn_zoom_out)

        self.btn_zoom_fit = QPushButton("🎯 Fit")
        self.btn_zoom_fit.setToolTip("Reset Zoom & Rotation to Fit Screen")
        self.btn_zoom_fit.clicked.connect(self.reset_zoom)
        self.btn_zoom_fit.setEnabled(False)
        top_layout.addWidget(self.btn_zoom_fit)

        # Options Menu
        self.btn_menu = QPushButton("⋮ Options")
        self.btn_menu.setStyleSheet("font-size: 15px; font-weight: bold; padding: 5px 14px;")
        
        self.options_menu = QMenu(self)
        
        action_open_file = QAction("📂 Open File...", self)
        action_open_file.triggered.connect(self.open_file_dialog)
        self.options_menu.addAction(action_open_file)

        action_open_folder = QAction("📁 Open Folder...", self)
        action_open_folder.triggered.connect(self.open_folder_dialog)
        self.options_menu.addAction(action_open_folder)

        self.options_menu.addSeparator()

        action_convert = QAction("🔄 Convert Image to .mj", self)
        action_convert.triggered.connect(self.convert_image_dialog)
        self.options_menu.addAction(action_convert)

        action_save_as = QAction("💾 Save / Export As...", self)
        action_save_as.triggered.connect(self.export_image_dialog)
        self.options_menu.addAction(action_save_as)

        self.options_menu.addSeparator()

        action_details = QAction("ℹ️ File Details", self)
        action_details.triggered.connect(self.show_details)
        self.options_menu.addAction(action_details)

        action_about = QAction("ℹ️ About", self)
        action_about.triggered.connect(self.show_about_dialog)
        self.options_menu.addAction(action_about)

        self.btn_menu.setMenu(self.options_menu)
        top_layout.addWidget(self.btn_menu)

        main_layout.addWidget(top_bar)

        self.scene = QGraphicsScene(self)
        self.view = SmoothGraphicsView(self.scene, self)
        self.view.setStyleSheet("background-color: #11111b; border: none;")
        
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)

        main_layout.addWidget(self.view)

        QShortcut(QKeySequence(Qt.Key.Key_Left), self, self.show_prev_image)
        QShortcut(QKeySequence(Qt.Key.Key_Right), self, self.show_next_image)
        QShortcut(QKeySequence(Qt.Key.Key_R), self, self.rotate_image)

    def rotate_image(self):
        if self.current_file_path:
            self.current_rotation = (self.current_rotation + 90) % 360
            self.pixmap_item.setRotation(self.current_rotation)
            self.scene.setSceneRect(self.pixmap_item.boundingRect())
            self.view.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)

    def zoom_in(self):
        if self.current_file_path:
            self.view.scale(1.15, 1.15)

    def zoom_out(self):
        if self.current_file_path:
            self.view.scale(1 / 1.15, 1 / 1.15)

    def reset_zoom(self):
        if self.current_file_path:
            self.current_rotation = 0
            self.pixmap_item.setRotation(0)
            self.view.resetTransform()
            self.view.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)

    def decode_mj(self, file_path):
        with open(file_path, 'rb') as f:
            header = f.read(16)
            if len(header) < 16:
                raise ValueError("Header missing or corrupted.")

            magic, width, height = struct.unpack('>8sII', header)
            if magic != b'MJFORMAT':
                raise ValueError("Not a valid .mj image format!")

            encrypted_data = f.read()

        decrypted_pixels = bytes(b ^ SECRET_KEY for b in encrypted_data)
        return Image.frombytes('RGB', (width, height),
