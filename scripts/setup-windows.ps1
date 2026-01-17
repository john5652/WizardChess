Write-Host "Wizard Chess setup (Windows)"
Write-Host "1) Install Godot 4.x (recommended 4.3 or 4.4) from https://godotengine.org/"
Write-Host "2) Open the project folder in Godot and run the main scene (once created)."
Write-Host ""
Write-Host "Checks:"
if (Get-Command git -ErrorAction SilentlyContinue) {
  Write-Host "✅ git found"
} else {
  Write-Host "⚠️ git not found (install Git for Windows)"
}
Write-Host "Done."
