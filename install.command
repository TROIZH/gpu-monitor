#!/bin/zsh
set -e

SCRIPT_DIR="${0:A:h}"

cd "$SCRIPT_DIR"

if ! command -v swiftc >/dev/null 2>&1; then
  echo "Swift compiler not found. Install Xcode Command Line Tools first:"
  echo "xcode-select --install"
  exit 1
fi

chmod +x macos-menu-bar/build-menu-app.command
macos-menu-bar/build-menu-app.command
open "$HOME/Applications/GPU Monitor.app"

echo ""
echo "GPU Monitor installed to: $HOME/Applications/GPU Monitor.app"
echo "A menu bar icon should now appear near Wi-Fi and battery."
