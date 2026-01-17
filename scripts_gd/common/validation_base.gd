extends Node

## Base script for validation scenes
## Provides common functionality like returning to the hub

func _on_back_button_pressed() -> void:
	var scene_path := "res://scenes/_validation/ValidationHub.tscn"
	var err := get_tree().change_scene_to_file(scene_path)
	if err != OK:
		push_error("ValidationBase: failed to change scene to '%s' (err=%s)" % [scene_path, err])
