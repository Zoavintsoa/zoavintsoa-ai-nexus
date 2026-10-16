#!/bin/sh
set -eu
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"
if [ "$(uname -s)" != "Darwin" ]; then
  echo "This builder must run on macOS." >&2
  exit 2
fi
ARCH="$(uname -m)"
if [ "$ARCH" != "x86_64" ]; then
  echo "This release must be built on an Intel macOS runner (x86_64); found: $ARCH" >&2
  exit 2
fi
python3 -m pip install --upgrade ".[desktop]"
python3 -m PyInstaller --noconfirm --clean --windowed \
  --name "Zoavintsoa AI Nexus" \
  --osx-bundle-identifier "com.zoavintsoa.ai-nexus" \
  --add-data "src/nexus/ui:nexus/ui" \
  --paths src src/nexus/desktop.py
APP="dist/Zoavintsoa AI Nexus.app"
if [ ! -d "$APP" ]; then
  echo "PyInstaller did not produce the expected app bundle." >&2
  exit 3
fi
EXECUTABLE="$APP/Contents/MacOS/Zoavintsoa AI Nexus"
if [ ! -f "$EXECUTABLE" ] || ! file "$EXECUTABLE" | grep -q "x86_64"; then
  echo "The generated app executable is not an Intel x86_64 binary." >&2
  file "$EXECUTABLE" >&2 || true
  exit 4
fi
mkdir -p dist/dmg-root
cp -R "$APP" dist/dmg-root/
ln -s /Applications dist/dmg-root/Applications
hdiutil create -volname "Zoavintsoa AI Nexus" -srcfolder dist/dmg-root \
  -ov -format UDZO "dist/Zoavintsoa-AI-Nexus-macOS.dmg"
echo "Created dist/Zoavintsoa-AI-Nexus-macOS.dmg (Intel x86_64)"
