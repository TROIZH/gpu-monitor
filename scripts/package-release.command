#!/bin/zsh
set -e

SCRIPT_DIR="${0:A:h}"
ROOT="${SCRIPT_DIR:h}"
VERSION="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' "$ROOT/macos-menu-bar/Info.plist")"
DIST="$ROOT/dist"
APP_BUILD="$ROOT/macos-menu-bar/build/GPU Monitor.app"
ZIP_PATH="$DIST/GPU-Monitor-v$VERSION.zip"
DMG_PATH="$DIST/GPU-Monitor-v$VERSION.dmg"

cd "$ROOT"
chmod +x macos-menu-bar/build-menu-app.command
macos-menu-bar/build-menu-app.command

rm -rf "$DIST"
mkdir -p "$DIST"

ditto -c -k --keepParent "$APP_BUILD" "$ZIP_PATH"

if command -v hdiutil >/dev/null 2>&1; then
  rm -f "$DMG_PATH"
  hdiutil create \
    -volname "GPU Monitor" \
    -srcfolder "$APP_BUILD" \
    -ov \
    -format UDZO \
    "$DMG_PATH" >/dev/null
fi

echo "Release artifacts:"
echo "$ZIP_PATH"
if [[ -f "$DMG_PATH" ]]; then
  echo "$DMG_PATH"
fi
