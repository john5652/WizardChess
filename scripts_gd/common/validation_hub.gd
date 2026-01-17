extends Control

## Validation Hub - Main navigation scene for asset validation
## Provides buttons to navigate to each validation scene

func _goto(scene_path: String) -> void:
	var err := get_tree().change_scene_to_file(scene_path)
	if err != OK:
		push_error("ValidationHub: failed to change scene to '%s' (err=%s)" % [scene_path, err])

func _on_interior_button_pressed() -> void:
	_goto("res://scenes/_validation/ValidateInterior.tscn")

func _on_exterior_button_pressed() -> void:
	_goto("res://scenes/_validation/ValidateExterior.tscn")

func _on_characters_button_pressed() -> void:
	_goto("res://scenes/_validation/ValidateCharacters.tscn")

func _on_chess_button_pressed() -> void:
	_goto("res://scenes/_validation/ValidateChess.tscn")

func _on_ui_button_pressed() -> void:
	_goto("res://scenes/_validation/ValidateUI.tscn")

func _on_back_button_pressed() -> void:
	# This button is only visible in validation scenes, not in hub
	# If called from hub, it does nothing (or could exit to main menu later)
	pass
