# Wizard Chess - Project Status

## Current Milestone
**Phase 2.1 Asset Validation scenes created (pending manual slicing where needed)**

## Current Scope
Wizard-themed chess RPG built with Godot 4, featuring:
- Top-down academy exploration
- NPC-triggered chess battles
- Guided chess learning progression

## What Works
- Project structure initialized
- Directory organization in place
- Setup scripts for macOS and Windows
- Documentation files in place
- Test sprites created for all asset types
- Validation scenes created and working:
  - ValidationHub.tscn - Navigation hub for all validation scenes
  - ValidateInterior.tscn - Interior tileset preview (64x64 tiles)
  - ValidateExterior.tscn - Exterior tileset preview (64x64 tiles)
  - ValidateCharacters.tscn - Player and NPC sprites with animations
  - ValidateChess.tscn - Chess board and pieces preview
  - ValidateUI.tscn - UI elements preview with proper slicing

## What's Next
- Replace test sprites with actual game artwork:
  - Create proper character spritesheets with animations
  - Design interior and exterior tilesets
  - Create UI kit with proper panels, buttons, and icons
  - Design chess pieces and board
- Create main game scenes
- Implement basic academy exploration
- Build chess battle system

## How to Run

### macOS
1. Ensure Godot 4.x (recommended 4.3 or 4.4) is installed from https://godotengine.org/
2. Run setup script: `./scripts/setup-mac.sh`
3. Open the project folder in Godot
4. Run the main scene (once created)

### Windows
1. Ensure Godot 4.x (recommended 4.3 or 4.4) is installed from https://godotengine.org/
2. Run setup script: `.\scripts\setup-windows.ps1`
3. Open the project folder in Godot
4. Run ValidationHub.tscn to preview assets, or run the main scene (once created)

## Validation Scenes
To preview and validate assets:
1. Open the project in Godot 4.x
2. Run `scenes/_validation/ValidationHub.tscn`
3. Use the buttons to navigate between validation scenes
4. Check asset scale, clarity, and organization
5. Note any TODO comments indicating manual slicing requirements
