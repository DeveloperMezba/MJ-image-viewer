#!/usr/bin/env bash

# ==============================================================================
# MJ Image Viewer Installer
# Developer: Mezba
# GitHub Repository: https://github.com/DeveloperMezba/MJ-image-viewer
# ==============================================================================

set -e

echo "--------------------------------------------------------"
echo "  Installing MJ Image Viewer (Developer: Mezba)..."
echo "--------------------------------------------------------"

# ১. প্রয়োজনীয় প্যাকেজ ইনস্টল
echo "[1/4] Installing dependencies..."
sudo apt update -y
sudo apt install -y python3-pyqt6 python3-pil xdg-utils curl git

# ২. ইনস্টলেশন ফোল্ডার তৈরি
INSTALL_DIR="$HOME/MJ_Viewer"
echo "[2/4] Setting up installation directory at $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"

# ৩. ক্যাশ বাইপাস করে গিটহাব থেকে সরাসরি mj_viewer_app.py ডাউনলোড
RAW_PY_URL="https://raw.githubusercontent.com/DeveloperMezba/MJ-image-viewer/main/mj_viewer_app.py?v=$(date +%s)"
echo "[3/4] Downloading mj_viewer_app.py from GitHub..."

curl -sSL "$RAW_PY_URL" -o "$INSTALL_DIR/mj_viewer_app.py"
chmod +x "$INSTALL_DIR/mj_viewer_app.py"

# ৪. ডেস্কটপ লঞ্চার ও ফাইল ফরম্যাট অ্যাসোসিয়েশন তৈরি
echo "[4/4] Creating Desktop Shortcut and associating .mj extension..."
APPS_DIR="$HOME/.local/share/applications"
mkdir -p "$APPS_DIR"

cat << EOF > "$APPS_DIR/mj_viewer.desktop"
[Desktop Entry]
Name=MJ Image Viewer
Comment=Custom .mj Image Format Viewer and Converter
Exec=/usr/bin/python3 $INSTALL_DIR/mj_viewer_app.py %f
Terminal=false
Type=Application
Icon=image-viewer
MimeType=image/x-mj;
Categories=Graphics;
EOF

chmod +x "$APPS_DIR/mj_viewer.desktop"
xdg-mime default mj_viewer.desktop image/x-mj

echo "--------------------------------------------------------"
echo " Installation Complete! App Name: MJ Image Viewer"
echo " Developer: DeveloerMezba"
echo "--------------------------------------------------------"
