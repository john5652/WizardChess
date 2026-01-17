# Wizard Chess – Cursor Project Rules

## Primary Goal
Build a cross-platform (Windows + macOS) Godot 4 project for a wizard-themed chess RPG with:
- top-down academy exploration
- NPC-triggered chess battles
- guided chess learning progression

## Non-Negotiables
- Keep everything cross-platform (no OS-specific hard paths).
- Prefer simple, readable Godot patterns over clever abstractions.
- Always update docs when adding dependencies or changing structure.

## Required Files (always keep current)
1) PROJECT_STATUS.md
- Current scope, what works, what's next, how to run

2) /scripts/setup-mac.sh and /scripts/setup-windows.ps1
- Install dependencies or validate environment
- If no dependencies, scripts should still perform checks and print guidance

## Godot Conventions
- Use Godot 4.x, GDScript.
- Scenes in `/scenes`, scripts in `/scripts_gd`, art in `/assets`.
- Use consistent naming:
  - snake_case for files
  - PascalCase for scene roots/classes

## Asset Handling Rules
- Do NOT edit original generated art in-place.
- Store originals under `/assets/_raw/`.
- Store cleaned/usable versions under `/assets/<category>/`.
- If slicing is needed, create `.tres` resources in `/assets/_imported/`.

## Git Rules
- Include a .gitignore appropriate for Godot 4.
- Commit after each milestone:
  - "init project shell"
  - "import assets"
  - "art validation scenes"
