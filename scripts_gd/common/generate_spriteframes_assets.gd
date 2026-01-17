extends SceneTree

## Generates SpriteFrames resources using Godot APIs (guaranteed compatible with current Godot version).
##
## Run:
##   godot --headless --path <project> --script res://scripts_gd/common/generate_spriteframes_assets.gd

func _save(res: Resource, path: String) -> void:
	var err := ResourceSaver.save(res, path)
	if err != OK:
		push_error("FAILED saving %s (err=%s)" % [path, err])
	else:
		print("Saved: ", path)


func _atlas(tex: Texture2D, x: int, y: int, w: int, h: int, flip_h: bool = false) -> Texture2D:
	var at := AtlasTexture.new()
	at.atlas = tex
	at.region = Rect2(x, y, w, h)
	at.flip_h = flip_h
	return at


func _build_player_frames(tex: Texture2D) -> SpriteFrames:
	# Layout: 4 columns, 3 rows (down/up/right). Each cell is 256x256.
	var frame := 256
	var frames := SpriteFrames.new()

	frames.add_animation("idle")
	frames.set_animation_loop("idle", true)
	frames.set_animation_speed("idle", 2.0)
	frames.add_frame("idle", _atlas(tex, 0, 0, frame, frame))

	var anims := {
		"walk_down": 0,
		"walk_up": 1,
		"walk_right": 2,
	}
	for anim_name in anims.keys():
		var row := int(anims[anim_name])
		frames.add_animation(anim_name)
		frames.set_animation_loop(anim_name, true)
		frames.set_animation_speed(anim_name, 8.0)
		for col in range(4):
			frames.add_frame(anim_name, _atlas(tex, col * frame, row * frame, frame, frame))

	# walk_left is flipped walk_right
	frames.add_animation("walk_left")
	frames.set_animation_loop("walk_left", true)
	frames.set_animation_speed("walk_left", 8.0)
	for col in range(4):
		frames.add_frame("walk_left", _atlas(tex, col * frame, 2 * frame, frame, frame, true))

	return frames


func _build_npc_frames(tex: Texture2D, npc_index: int) -> SpriteFrames:
	# Layout: 3 NPCs across, each NPC uses 2 columns (2 frames).
	# Rows: down/up/right. Cell size: 256x256.
	var frame := 256
	var start_col := npc_index * 2
	var frames := SpriteFrames.new()

	frames.add_animation("idle")
	frames.set_animation_loop("idle", true)
	frames.set_animation_speed("idle", 2.0)
	frames.add_frame("idle", _atlas(tex, start_col * frame, 0, frame, frame))

	var anims := {
		"walk_down": 0,
		"walk_up": 1,
		"walk_right": 2,
	}
	for anim_name in anims.keys():
		var row := int(anims[anim_name])
		frames.add_animation(anim_name)
		frames.set_animation_loop(anim_name, true)
		frames.set_animation_speed(anim_name, 6.0)
		for i in range(2):
			frames.add_frame(anim_name, _atlas(tex, (start_col + i) * frame, row * frame, frame, frame))

	frames.add_animation("walk_left")
	frames.set_animation_loop("walk_left", true)
	frames.set_animation_speed("walk_left", 6.0)
	for i in range(2):
		frames.add_frame("walk_left", _atlas(tex, (start_col + i) * frame, 2 * frame, frame, frame, true))

	return frames


func _initialize() -> void:
	print("Generating SpriteFrames via Godot API...")

	var player_tex := load("res://assets/characters/player/player_character_wizard.png") as Texture2D
	if player_tex == null:
		push_error("Missing player texture")
		quit(1)
		return
	_save(_build_player_frames(player_tex), "res://assets/_imported/player_frames.tres")

	var npc_tex := load("res://assets/characters/npcs/npc_sprites.png") as Texture2D
	if npc_tex == null:
		push_error("Missing npc texture")
		quit(1)
		return

	_save(_build_npc_frames(npc_tex, 0), "res://assets/_imported/npc1_frames.tres")
	_save(_build_npc_frames(npc_tex, 1), "res://assets/_imported/npc2_frames.tres")
	_save(_build_npc_frames(npc_tex, 2), "res://assets/_imported/npc3_frames.tres")

	print("Done generating SpriteFrames.")
	quit(0)

