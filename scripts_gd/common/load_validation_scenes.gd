extends SceneTree

## Headless helper to load/instance validation scenes and print errors.
## Run with:
##   godot --headless --path <project> --script res://scripts_gd/common/load_validation_scenes.gd

func _initialize() -> void:
	var scenes := PackedStringArray([
		"res://scenes/_validation/ValidationHub.tscn",
		"res://scenes/_validation/ValidateInterior.tscn",
		"res://scenes/_validation/ValidateExterior.tscn",
		"res://scenes/_validation/ValidateCharacters.tscn",
		"res://scenes/_validation/ValidateChess.tscn",
		"res://scenes/_validation/ValidateUI.tscn",
	])

	for p in scenes:
		print("\n--- Loading: ", p)
		if not ResourceLoader.exists(p):
			push_error("Missing scene file: %s" % p)
			continue

		var res := ResourceLoader.load(p)
		if res == null:
			push_error("FAILED to load resource: %s" % p)
			continue

		if res is PackedScene:
			var inst := (res as PackedScene).instantiate()
			if inst == null:
				push_error("FAILED to instantiate PackedScene: %s" % p)
			else:
				print("OK instanced root: ", inst.name, " type=", inst.get_class())
				inst.queue_free()
		else:
			push_error("Loaded resource is not a PackedScene: %s (%s)" % [p, res.get_class()])

	print("\nDone loading validation scenes.")
	quit(0)

