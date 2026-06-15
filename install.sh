#!/bin/zsh
set -euo pipefail

REPO="TROIZH/gpu-monitor"
APP_NAME="GPU Monitor.app"
INSTALL_DIR="$HOME/Applications"
TMP_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

echo "GPU Monitor installer"
echo "Fetching latest release from GitHub..."

LATEST_JSON="$(curl -fsSL "https://api.github.com/repos/$REPO/releases/latest")"
DOWNLOAD_URL="$(printf '%s' "$LATEST_JSON" | awk -F '"' '/browser_download_url/ && /GPU-Monitor-v.*\\.zip/ { print $4; exit }')"

if [[ -z "${DOWNLOAD_URL:-}" ]]; then
  echo "Could not find a GPU Monitor zip asset in the latest GitHub Release."
  echo "Open manually: https://github.com/$REPO/releases/latest"
  exit 1
fi

ZIP_PATH="$TMP_DIR/gpu-monitor.zip"
echo "Downloading: $DOWNLOAD_URL"
curl -fL "$DOWNLOAD_URL" -o "$ZIP_PATH"

echo "Installing to $INSTALL_DIR..."
ditto -x -k "$ZIP_PATH" "$TMP_DIR"
APP_PATH="$(find "$TMP_DIR" -maxdepth 3 -name "$APP_NAME" -type d | head -n 1)"

if [[ -z "${APP_PATH:-}" ]]; then
  echo "Downloaded archive did not contain $APP_NAME."
  exit 1
fi

mkdir -p "$INSTALL_DIR"
rm -rf "$INSTALL_DIR/$APP_NAME"
cp -R "$APP_PATH" "$INSTALL_DIR/$APP_NAME"

echo "Opening GPU Monitor..."
open "$INSTALL_DIR/$APP_NAME"

echo ""
echo "Installed: $INSTALL_DIR/$APP_NAME"
echo "If macOS blocks the unsigned prototype, right-click the app in Finder and choose Open."
