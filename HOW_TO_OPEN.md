# How to Open Wizard Chess in Godot 4

## Step-by-Step Instructions

### Prerequisites
1. **Install Godot 4.x** (recommended 4.3 or 4.4)
   - Download from: https://godotengine.org/download
   - Choose the version for your operating system (macOS or Windows)

### Opening the Project

#### Option 1: Open from Godot Project Manager (Recommended)

1. **Launch Godot 4.x**
   - Double-click the Godot executable you downloaded
   - The Godot Project Manager window will open

2. **Import/Open the Project**
   - Click **"Import"** or **"Open"** button (depending on your Godot version)
   - Navigate to: `/Users/ellerion/Desktop/Cursor Projects/WizardChess`
   - Select the folder (the one containing `project.godot`)
   - Click **"Open"** or **"Select Folder"**

3. **Run the Project**
   - The project should appear in your project list
   - Click **"Run"** (play button) or press `F5`
   - The ValidationHub scene will open automatically

#### Option 2: Open Directly from File System

1. **Navigate to Project Folder**
   - Open Finder (macOS) or File Explorer (Windows)
   - Go to: `/Users/ellerion/Desktop/Cursor Projects/WizardChess`

2. **Open with Godot**
   - **macOS**: Right-click `project.godot` → "Open With" → Select Godot
   - **Windows**: Right-click `project.godot` → "Open with" → Select Godot
   - Or drag the `project.godot` file onto the Godot executable

3. **Run the Project**
   - Click the **Play** button (▶) in the top-right corner
   - Or press `F5`

### Project Structure Verification

The project should have:
- ✅ `project.godot` - Main project file (in root directory)
- ✅ `icon.svg` - Project icon
- ✅ `scenes/_validation/` - Validation scenes folder
- ✅ `scripts_gd/` - GDScript files folder
- ✅ `assets/` - Game assets folder

### Troubleshooting

**Problem: "Project file not found"**
- Make sure you're opening the folder that contains `project.godot`
- The file should be in: `/Users/ellerion/Desktop/Cursor Projects/WizardChess/project.godot`

**Problem: "Scene not found" errors**
- Make sure all files are in the correct locations
- Check that `scenes/_validation/ValidationHub.tscn` exists

**Problem: Assets not loading**
- Godot will import assets automatically on first open
- Wait for the import process to complete (check bottom-right status bar)
- If assets show as missing, verify paths in the FileSystem panel

### What to Expect

When you run the project:
1. The **ValidationHub** scene will open
2. You'll see buttons for:
   - Interior Tileset
   - Exterior Tileset
   - Characters
   - Chess
   - UI Elements
3. Click any button to view that asset validation scene
4. Use "Back to Hub" button to return to the main menu

### Next Steps

After opening the project:
1. Explore the validation scenes to preview assets
2. Check TODO comments in scenes for manual slicing requirements
3. Adjust TileMap configurations if needed
4. Begin creating gameplay scenes when ready
