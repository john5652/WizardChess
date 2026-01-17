#!/usr/bin/env bash
set -euo pipefail

echo "Wizard Chess setup (macOS)"
echo "1) Install Godot 4.x (recommended 4.3 or 4.4) from https://godotengine.org/"
echo "2) Open the project folder in Godot and run the main scene (once created)."
echo ""
echo "Checks:"
if command -v git >/dev/null 2>&1; then
  echo "✅ git found"
else
  echo "⚠️ git not found (install Xcode Command Line Tools: xcode-select --install)"
fi

echo "Done."
