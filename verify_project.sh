#!/bin/bash

# Wizard Chess - Project Verification Script
# Verifies project structure is correct

echo "=== Wizard Chess Project Verification ==="
echo ""

PROJECT_ROOT="/Users/ellerion/Desktop/Cursor Projects/WizardChess"
cd "$PROJECT_ROOT" || exit 1

echo "Project root: $PROJECT_ROOT"
echo ""

# Check project.godot
if [ -f "project.godot" ]; then
    echo "✅ project.godot exists"
    MAIN_SCENE=$(grep "run/main_scene" project.godot | cut -d'=' -f2 | tr -d '"')
    if [ -n "$MAIN_SCENE" ]; then
        echo "   Main scene: $MAIN_SCENE"
        if [ -f "$MAIN_SCENE" ]; then
            echo "   ✅ Main scene file exists"
        else
            echo "   ⚠️  Main scene file NOT found at: $MAIN_SCENE"
        fi
    fi
else
    echo "❌ project.godot MISSING"
fi

echo ""

# Check scenes
echo "Checking scenes..."
SCENE_COUNT=$(find scenes/_validation -name "*.tscn" 2>/dev/null | wc -l | tr -d ' ')
if [ "$SCENE_COUNT" -eq 6 ]; then
    echo "✅ Found $SCENE_COUNT validation scenes"
else
    echo "⚠️  Found $SCENE_COUNT validation scenes (expected 6)"
fi

# Check scripts
echo ""
echo "Checking scripts..."
SCRIPT_COUNT=$(find scripts_gd/common -name "*.gd" 2>/dev/null | wc -l | tr -d ' ')
if [ "$SCRIPT_COUNT" -ge 3 ]; then
    echo "✅ Found $SCRIPT_COUNT common scripts"
else
    echo "⚠️  Found $SCRIPT_COUNT common scripts (expected at least 3)"
fi

# Check assets
echo ""
echo "Checking assets..."
if [ -d "assets" ]; then
    echo "✅ assets/ directory exists"
    ASSET_COUNT=$(find assets -name "*.png" 2>/dev/null | wc -l | tr -d ' ')
    echo "   Found $ASSET_COUNT PNG files"
else
    echo "❌ assets/ directory MISSING"
fi

echo ""
echo "=== Verification Complete ==="
echo ""
echo "If all checks passed, try:"
echo "1. Open this folder in Godot: $PROJECT_ROOT"
echo "2. Wait for import to complete (check bottom-right status bar)"
echo "3. If files don't appear, delete .godot folder and reopen:"
echo "   rm -rf .godot"
echo ""
