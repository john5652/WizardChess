# Troubleshooting: Godot Not Showing Files

## Problem: "No scene has ever been identified" and empty FileSystem

This usually means Godot hasn't scanned/imported the project yet.

## Solution Steps

### Step 1: Verify You're Opening the Correct Folder

**IMPORTANT:** Open the **ROOT** directory, not the `wizard-chess` subdirectory.

**Correct path to open:**
```
/Users/ellerion/Desktop/Cursor Projects/WizardChess
```

**NOT this path:**
```
/Users/ellerion/Desktop/Cursor Projects/WizardChess/wizard-chess  ❌
```

### Step 2: Open Project in Godot

1. **Launch Godot 4.x**
2. **In Project Manager:**
   - Click **"Import"** button
   - Navigate to: `/Users/ellerion/Desktop/Cursor Projects/WizardChess`
   - **Select the folder** (the one containing `project.godot` in the root)
   - Click **"Open"** or **"Select Folder"**

### Step 3: Force Godot to Rescan (if files still don't appear)

If the FileSystem panel is still empty:

1. **Close Godot completely**
2. **Delete the `.godot` folder** (if it exists in the root):
   ```bash
   cd "/Users/ellerion/Desktop/Cursor Projects/WizardChess"
   rm -rf .godot
   ```
3. **Reopen the project in Godot**
4. **Wait for import to complete** - Look at the bottom-right status bar
   - You should see "Importing..." messages
   - This may take a minute or two

### Step 4: Verify Project Structure

After opening, you should see in the FileSystem panel:
- ✅ `scenes/` folder with `_validation/` subfolder
- ✅ `scripts_gd/` folder
- ✅ `assets/` folder
- ✅ `project.godot` file
- ✅ `icon.svg` file

### Step 5: Set Main Scene (if needed)

If Godot still says "no scene has been identified":

1. In the FileSystem panel, navigate to: `scenes/_validation/`
2. Right-click on `ValidationHub.tscn`
3. Select **"Set as Main Scene"**
4. Or manually set it in Project Settings:
   - Project → Project Settings → Application → Run → Main Scene
   - Set to: `res://scenes/_validation/ValidationHub.tscn`

## Common Issues

### Issue: Opening wrong folder
- **Symptom:** No files appear, or only a few files
- **Solution:** Make sure you're opening the root folder containing `project.godot`

### Issue: Godot hasn't imported yet
- **Symptom:** Files exist but FileSystem is empty
- **Solution:** Wait for import to complete, or delete `.godot` folder and reopen

### Issue: Scene path incorrect
- **Symptom:** "Scene not found" error
- **Solution:** Verify `scenes/_validation/ValidationHub.tscn` exists

## Quick Verification

Run this in terminal to verify structure:
```bash
cd "/Users/ellerion/Desktop/Cursor Projects/WizardChess"
ls -la project.godot  # Should exist
ls scenes/_validation/*.tscn  # Should show 6 scene files
ls scripts_gd/common/*.gd  # Should show 3 script files
```

If all these commands work, the project structure is correct and the issue is with Godot's scanning.
