extends SceneTree

@export var resource_path: String = "res://assets/_imported/player_frames.tres"

func _initialize() -> void:
	print("Loading resource: ", resource_path)
	var res := ResourceLoader.load(resource_path)
	if res == null:
		push_error("FAILED to load: %s" % resource_path)
	else:
		print("OK type=", res.get_class())
	quit(0)

