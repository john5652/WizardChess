extends TileMap

## Fills a small preview grid at runtime so we don't have to embed TileMap tile_data in the .tscn.
## This avoids fragile text serialization and works across Godot versions.

@export var preview_cols: int = 12
@export var preview_rows: int = 8
@export var source_id: int = 0

func _ready() -> void:
	if tile_set == null:
		push_error("TileMapPreview: missing TileSet on %s" % name)
		return

	clear()

	# Best-effort fill: atlas coords (x,y) typically map 1:1 to TileSetAtlasSource coords.
	for y in range(preview_rows):
		for x in range(preview_cols):
			set_cell(0, Vector2i(x, y), source_id, Vector2i(x, y))

