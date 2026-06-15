#!/bin/zsh
set -e

SCRIPT_DIR="${0:A:h}"
ROOT="${SCRIPT_DIR:h}"
SRC="$ROOT/macos-menu-bar/GPUStatusMenu.swift"
PLIST="$ROOT/macos-menu-bar/Info.plist"
BUILD="$ROOT/macos-menu-bar/build"
APP="$BUILD/GPU Monitor.app"
RESOURCES="$APP/Contents/Resources"
INSTALL_DIR="$HOME/Applications"
INSTALLED_APP="$INSTALL_DIR/GPU Monitor.app"

rm -rf "$BUILD"
mkdir -p "$APP/Contents/MacOS"
mkdir -p "$RESOURCES"
cp "$PLIST" "$APP/Contents/Info.plist"
cp "$ROOT/README.md" "$RESOURCES/README.md"

rsync -a --delete \
  --exclude ".venv" \
  --exclude "__pycache__" \
  --exclude "*.pyc" \
  --exclude "*.sqlite3" \
  --exclude "*.log" \
  "$ROOT/local-resource-monitor-backend/" \
  "$RESOURCES/local-resource-monitor-backend/"

rsync -a --delete \
  --exclude ".DS_Store" \
  "$ROOT/gpu-monitor-frontend-inspect/" \
  "$RESOURCES/gpu-monitor-frontend-inspect/"

swiftc "$SRC" \
  -framework AppKit \
  -framework WebKit \
  -o "$APP/Contents/MacOS/GPU Monitor"

chmod +x "$APP/Contents/MacOS/GPU Monitor"
mkdir -p "$INSTALL_DIR"
rm -rf "$INSTALLED_APP"
cp -R "$APP" "$INSTALLED_APP"

echo "Installed: $INSTALLED_APP"
