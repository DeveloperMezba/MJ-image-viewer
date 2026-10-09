import sys
import os
import struct
import json
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
        return Image.frombytes('RGB', (width, height), decrypted_pixels), width, height

    def encode_to_mj(self, input_path, output_path):
        img = Image.open(input_path).convert('RGB')
        width, height = img.size
        raw_pixels = bytearray(img.tobytes())

        encrypted_pixels = bytearray(b ^ SECRET_KEY for b in raw_pixels)
        header = struct.pack('>8sII', b'MJFORMAT', width, height)

        with open(output_path, 'wb') as f:
            f.write(header)
            f.write(encrypted_pixels)

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Supported Images (*.mj *.png *.jpg *.jpeg *.webp *.bmp *.gif);;MJ Images (*.mj);;All Files (*)"
        )
        if file_path:
            self.load_file(file_path)

    def open_folder_dialog(self):
        folder_dir = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_dir:
            files = [
                os.path.join(folder_dir, f) for f in os.listdir(folder_dir)
                if f.lower().endswith(SUPPORTED_EXTENSIONS)
            ]
            files.sort(key=lambda x: x.lower())
            if files:
                self.folder_files = files
                self.current_index = 0
                self.load_file(self.folder_files[0], update_folder=False)
            else:
                QMessageBox.information(self, "No Images", "No supported images found in this folder.")

    def convert_image_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image to Convert to .MJ",
            "",
            "Standard Images (*.png *.jpg *.jpeg *.webp *.bmp *.gif);;All Files (*)"
        )
        if not file_path:
            return

        base_name = os.path.splitext(file_path)[0]
        default_output = base_name + ".mj"

        try:
            self.encode_to_mj(file_path, default_output)
            QMessageBox.information(
                self, 
                "Conversion Successful", 
                f"Successfully converted to .mj format!\n\nSaved at:\n{default_output}"
            )
            self.load_file(default_output)

        except Exception as e:
            QMessageBox.critical(self, "Conversion Error", f"Failed to convert image:\n{str(e)}")

    def export_image_dialog(self):
        if not self.loaded_pil_image:
            QMessageBox.warning(self, "Export Error", "No image loaded to export.")
            return

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Image As",
            "",
            "PNG Image (*.png);;JPEG Image (*.jpg *.jpeg);;BMP Image (*.bmp)"
        )
        if save_path:
            try:
                self.loaded_pil_image.save(save_path)
                QMessageBox.information(self, "Success", f"Image exported successfully to:\n{save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", str(e))

    def scan_folder(self, current_file):
        folder_dir = os.path.dirname(current_file)
        try:
            files = [
                os.path.join(folder_dir, f) for f in os.listdir(folder_dir)
                if f.lower().endswith(SUPPORTED_EXTENSIONS)
            ]
            files.sort(key=lambda x: x.lower())
            self.folder_files = files
            self.current_index = self.folder_files.index(current_file) if current_file in self.folder_files else -1
        except Exception:
            self.folder_files = [current_file]
            self.current_index = 0

        self.update_nav_buttons()

    def update_nav_buttons(self):
        has_multiple = len(self.folder_files) > 1
        self.btn_prev.setEnabled(has_multiple)
        self.btn_next.setEnabled(has_multiple)

    def show_prev_image(self):
        if self.folder_files and self.current_index > 0:
            self.current_index -= 1
            self.load_file(self.folder_files[self.current_index], update_folder=False)

    def show_next_image(self):
        if self.folder_files and self.current_index < len(self.folder_files) - 1:
            self.current_index += 1
            self.load_file(self.folder_files[self.current_index], update_folder=False)

    def load_file(self, file_path, update_folder=True):
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            file_size_bytes = os.path.getsize(file_path)

            if file_size_bytes < 1024 * 1024:
                size_str = f"{file_size_bytes / 1024:.2f} KB"
            else:
                size_str = f"{file_size_bytes / (1024 * 1024):.2f} MB"

            if file_ext == '.mj':
                img, width, height = self.decode_mj(file_path)
                format_name = "MJ Image Format (.mj)"
            else:
                img = Image.open(file_path).convert('RGB')
                width, height = img.size
                format_name = f"Standard Image ({file_ext.upper()})"

            self.loaded_pil_image = img
            self.current_file_path = file_path
            self.current_rotation = 0

            data = img.tobytes("raw", "RGB")
            qimg = QImage(data, width, height, width * 3, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)

            self.pixmap_item.setPixmap(pixmap)
            self.pixmap_item.setRotation(0)
            
            self.pixmap_item.setTransformOriginPoint(width / 2, height / 2)
            self.scene.setSceneRect(0, 0, width, height)
            self.view.resetTransform()
            self.view.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)

            self.image_info = {
                "File Name": os.path.basename(file_path),
                "Format": format_name,
                "Dimensions": f"{width} × {height} pixels",
                "File Size": size_str,
                "Location": file_path
            }

            if update_folder:
                self.scan_folder(file_path)

            counter_str = f" ({self.current_index + 1}/{len(self.folder_files)})" if self.folder_files else ""
            self.lbl_status.setText(f"{os.path.basename(file_path)}{counter_str}")
            self.btn_rotate.setEnabled(True)
            self.btn_zoom_in.setEnabled(True)
            self.btn_zoom_out.setEnabled(True)
            self.btn_zoom_fit.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Error Opening File", f"Could not open image:\n{str(e)}")

    def show_details(self):
        if not self.image_info:
            QMessageBox.information(self, "File Details", "No image currently loaded.")
            return

        info_msg = (
            f"<b>File Name:</b> {self.image_info['File Name']}<br><br>"
            f"<b>Format:</b> {self.image_info['Format']}<br>"
            f"<b>Resolution:</b> {self.image_info['Dimensions']}<br>"
            f"<b>File Size:</b> {self.image_info['File Size']}<br><br>"
            f"<b>Full Path:</b><br><small>{self.image_info['Location']}</small>"
        )

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Image Details")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(info_msg)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()

    # ==============================================================================
    # FIXED GITHUB AUTO-UPDATE SYSTEM
    # ==============================================================================
    def show_about_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("About MJ Image Viewer")
        dialog.setFixedSize(380, 240)
        dialog.setStyleSheet("background-color: #2b2b3b; color: #eceff4;")

        layout = QVBoxLayout(dialog)
        
        lbl_title = QLabel("<h2>MJ Image Viewer</h2>")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)

        lbl_dev = QLabel(f"<b>Developer:</b> {DEVELOPER_NAME}<br><b>Current Version:</b> {CURRENT_VERSION}")
        lbl_dev.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_dev.setStyleSheet("font-size: 13px;")
        layout.addWidget(lbl_dev)

        btn_update = QPushButton("🚀 Check for Updates")
        btn_update.setStyleSheet("""
            QPushButton {
                background-color: #5e81ac;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #81a1c1; }
        """)
        btn_update.clicked.connect(self.check_for_updates)
        layout.addWidget(btn_update)

        dialog.exec()

    def check_for_updates(self):
        try:
            req = urllib.request.Request(GITHUB_REPO_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    latest_version = data.get("tag_name", CURRENT_VERSION)

                    if latest_version != CURRENT_VERSION:
                        reply = QMessageBox.question(
                            self,
                            "Update Available!",
                            f"New version <b>{latest_version}</b> is available!<br>Current version: {CURRENT_VERSION}<br><br>Do you want to update now?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                        )
                        if reply == QMessageBox.StandardButton.Yes:
                            self.perform_auto_update()
                    else:
                        QMessageBox.information(self, "No Updates", f"You are using the latest version ({CURRENT_VERSION}).")
        except Exception as e:
            QMessageBox.warning(self, "Update Check", f"Could not check for updates:\n{str(e)}")

    def perform_auto_update(self):
        try:
            # ইনস্টলড ফাইলের অরিজিনাল প্যাথ শনাক্ত করা
            script_path = os.path.realpath(__file__)
            
            req = urllib.request.Request(RAW_SCRIPT_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    new_code = response.read().decode('utf-8')
                    
                    # ১. ফাইল নিরাপদভাবে সেভ করা
                    with open(script_path, 'w', encoding='utf-8') as f:
                        f.write(new_code)
                    
                    # ২. পারমিশন নিশ্চিত করা (Executable Permission)
                    os.chmod(script_path, 0o755)

                    QMessageBox.information(
                        self, 
                        "Update Successful", 
                        "MJ Image Viewer has been updated successfully!\nClick OK to restart the application now."
                    )
                    
                    # ৩. বর্তমান অ্যাপ বন্ধ করে নতুন কোড দিয়ে সাথে সাথে অ্যাপ রি-লঞ্চ করা
                    python = sys.executable
                    os.execv(python, [python, script_path] + sys.argv[1:])

        except Exception as e:
            QMessageBox.critical(self, "Update Failed", f"Failed to perform auto update:\n{str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    file_to_open = sys.argv[1] if len(sys.argv) > 1 else None
    window = MJApp(file_to_open)
    window.show()
    sys.exit(app.exec())
