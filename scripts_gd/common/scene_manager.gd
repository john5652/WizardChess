extends Node

## Helper script for scene management and navigation
## Provides utility functions for switching between validation scenes

static func load_validation_scene(scene_name: String) -> void:
	var scene_path = "res://scenes/_validation/" + scene_name + ".tscn"
	if ResourceLoader.exists(scene_path):
		get_tree().change_scene_to_file(scene_path)
	else:
		push_error("Scene not found: " + scene_path)
