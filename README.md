# 🖼️ MJ Image Viewer

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg?style=for-the-badge&logo=python" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/GUI-PyQt6-orange.svg?style=for-the-badge&logo=qt" alt="PyQt6">
  <img src="https://img.shields.io/badge/Platform-Linux-lightgrey.svg?style=for-the-badge&logo=linux" alt="Linux">
  <img src="https://img.shields.io/badge/Developer-Mezba-purple.svg?style=for-the-badge" alt="Developer DeveloperMezba">
</p>

**MJ Image Viewer** is a fast, modern, and lightweight image viewer built with Python and PyQt6. It introduces support for a custom obfuscated image format (`.mj`), while offering seamless viewing, conversion, and inspection tools for standard image formats (`.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`, `.gif`).

---

## ⚡ Quick One-Line Installation (Linux)

You can install **MJ Image Viewer** instantly with a single command in your Linux terminal. This automatically sets up all dependencies, downloads the app, creates desktop shortcuts, and associates `.mj` files with the application.

```bash
curl -sSL https://raw.githubusercontent.com/DeveloperMezba/MJ-image-viewer/main/install.sh | bash
```

---

## ✨ Key Features

* 🔐 **Proprietary `.mj` Format Support:** Custom binary header validation (`MJFORMAT`) combined with key-protected pixel obfuscation for custom image protection.
* 🔄 **Built-in Format Converter:** Easily convert any standard image (`PNG`, `JPG`, `WEBP`, `BMP`, `GIF`) into `.mj` format directly from the application menu.
* 💾 **Image Export:** Save/Export `.mj` images back into standard formats (`PNG`, `JPEG`, `BMP`) at any time.
* 🔍 **Anti-Aliased High-Quality Rendering:** Hardware-accelerated image scaling with smooth filtering to eliminate visual noise and pixelation during zoom.
* 🔎 **Interactive Pan & Zoom:** Zoom in/out smoothly using your mouse wheel or control buttons, with drag-and-pan canvas interaction and 1-click **Fit to View**.
* 🔄 **Non-Destructive View Rotation:** Rotate images 90° clockwise on-the-fly (`R` key shortcut or top bar button) without modifying or re-saving the original file data.
* 📁 **Folder Navigation:** Next/Previous buttons and Left/Right arrow keys automatically index and cycle through all supported images in the current directory.
* ℹ️ **Metadata Inspector:** View comprehensive file parameters, including image resolution, file size, format type, and file system location.
* 🚀 **Seamless GitHub Auto-Update System:** Built-in update engine checks the latest GitHub release tags via API and updates the local script in 1 click.

---

## 🛠️ System Requirements

- **Operating System:** Linux (Ubuntu/Debian, Arch, Fedora, etc.)
- **Python:** `Python 3.8` or higher
- **Dependencies:**
  - `PyQt6`
  - `Pillow` (PIL)
  - `xdg-utils`
  - `curl` / `git`

---

## 📦 Manual Installation & Setup

If you prefer to clone the repository and install manually:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/DeveloperMezba/MJ-image-viewer.git
   cd MJ-image-viewer
   ```

2. **Grant execution permissions to the installer:**
   ```bash
   chmod +x install.sh
   ```

3. **Run the installer:**
   ```bash
   ./install.sh
   ```

---

## 🚀 Running Manually (Without Installation)

If you just want to run the application using Python directly:

```bash
# Install Python dependencies
pip install PyQt6 Pillow

# Launch the application
python3 mj_viewer_app.py
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut Key | Action |
| :--- | :--- |
| **`Left Arrow`** | Previous Image in Folder |
| **`Right Arrow`** | Next Image in Folder |
| **`R`** | Rotate Image View 90° Right |
| **`Mouse Wheel`** | Smooth Zoom In / Zoom Out |
| **`Click & Drag`** | Pan / Move Image Canvas |

---

## 🔄 Updating the App

To update to the latest version:
1. Open the application.
2. Click **`⋮ Options`** $\rightarrow$ **`ℹ️ About`**.
3. Click **`🚀 Check for Updates`**.
4. If a new version is available, the app will update itself automatically!

---

## 👨‍💻 Author & License

- **Developer:** [DeveloperMezba](https://github.com/DeveloperMezba)
- **GitHub Repository:** [https://github.com/DeveloperMezba/MJ-image-viewer](https://github.com/DeveloperMezba/MJ-image-viewer)
