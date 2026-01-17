#!/usr/bin/env python3
"""
Prepare WizardChess assets for Godot:
- Generate TileSet resources for 32x32 tilesets
- Generate SpriteFrames for player + NPCs
- Generate AtlasTextures for chess pieces + UI kit elements

IMPORTANT:
- This script **does not modify any PNGs**. It only regenerates `.tres` resources.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List, Tuple

from png_tools import read_png


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _rel_res(path: str) -> str:
	return "res://" + os.path.relpath(path, PROJECT_ROOT).replace(os.sep, "/")


def _get_texture_uid(import_file: str) -> str | None:
	if not os.path.exists(import_file):
		return None
	with open(import_file, "r", encoding="utf-8") as f:
		for line in f:
			if 'uid="' in line:
				return line.split('uid="', 1)[1].split('"', 1)[0]
	return None


def write_tileset(
	png_path: str,
	out_tres_path: str,
	tileset_uid: str,
	tile_size: int = 32,
) -> None:
	dims = read_png(png_path)
	w, h = dims.width, dims.height
	cols = w // tile_size
	rows = h // tile_size

	lines: List[str] = []
	lines += [f'[gd_resource type="TileSet" load_steps=3 format=3 uid="{tileset_uid}"]', ""]
	lines += [
		f'[ext_resource type="Texture2D" path="{_rel_res(png_path)}" id="1_texture"]',
		"",
		'[sub_resource type="TileSetAtlasSource" id="TileSetAtlasSource_1"]',
		'texture = ExtResource("1_texture")',
		f'texture_region_size = Vector2i({tile_size}, {tile_size})',
		"",
	]
	for y in range(rows):
		for x in range(cols):
			lines.append(f"{x}:{y}/0 = 0")
	lines += ["", "[resource]", f"tile_size = Vector2i({tile_size}, {tile_size})", 'sources/0 = SubResource("TileSetAtlasSource_1")']

	os.makedirs(os.path.dirname(out_tres_path), exist_ok=True)
	with open(out_tres_path, "w", encoding="utf-8") as f:
		f.write("\n".join(lines))


def write_spriteframes_player(
	png_path: str,
	out_tres_path: str,
	frames_uid: str,
	frame_size: int = 256,
	cols_used: int = 4,
	start_col: int = 0,
	start_row: int = 0,
) -> None:
	"""
	Player layout (based on your sheet):
	- 4 columns = animation frames
	- Rows:
	  0 = walk_down/front
	  1 = walk_up/back
	  2 = walk_right/side
	"""
	frames_per_anim = cols_used

	# subresource count: 1 idle + 3*frames + frames flipped
	sub_count = 1 + 3 * frames_per_anim + frames_per_anim
	load_steps = 2 + sub_count

	lines: List[str] = []
	lines += [f'[gd_resource type="SpriteFrames" load_steps={load_steps} format=3 uid="{frames_uid}"]', ""]
	lines += [
		f'[ext_resource type="Texture2D" path="{_rel_res(png_path)}" id="1_texture"]',
		"",
	]

	sub_blocks: List[str] = []

	def add_atlas(id_name: str, x: int, y: int, flip_h: bool = False) -> str:
		block = [
			f'[sub_resource type="AtlasTexture" id="{id_name}"]',
			'atlas = ExtResource("1_texture")',
			f"region = Rect2({x}, {y}, {frame_size}, {frame_size})",
		]
		if flip_h:
			block.append("flip_h = true")
		sub_blocks.append("\n".join(block))
		return id_name

	# idle = first frame of walk_down
	idle_id = add_atlas("at_idle", start_col * frame_size, start_row * frame_size, flip_h=False)

	def frames_for_row(prefix: str, row: int) -> List[str]:
		y = row * frame_size
		ids: List[str] = []
		for c in range(frames_per_anim):
			ids.append(add_atlas("%s_%d" % (prefix, c), (start_col + c) * frame_size, y, flip_h=False))
		return ids

	down = frames_for_row("at_down", start_row + 0)
	up = frames_for_row("at_up", start_row + 1)
	right = frames_for_row("at_right", start_row + 2)
	left: List[str] = []
	for c in range(frames_per_anim):
		left.append(add_atlas("at_left_%d" % c, (start_col + c) * frame_size, (start_row + 2) * frame_size, flip_h=True))

	# write subresources
	for i, block in enumerate(sub_blocks):
		if i > 0:
			lines.append("")
		lines.append(block)

	lines += ["", "[resource]", "animations = {"]  # Godot's SpriteFrames dict format
	lines += [
		'"idle": {',
		f'"frames": [SubResource("{idle_id}")],',
		'"loop": true,',
		'"speed": 2.0',
		"},",
	]

	def anim_block(name: str, ids: List[str]) -> List[str]:
		var_frames = ", ".join([f'SubResource("{i}")' for i in ids])
		return [
			f'"{name}": {{',
			f'"frames": [{var_frames}],',
			'"loop": true,',
			'"speed": 8.0',
			"},",
		]

	lines += anim_block("walk_down", down)
	lines += anim_block("walk_up", up)
	lines += anim_block("walk_right", right)
	lines += anim_block("walk_left", left)
	lines += ["}"]

	with open(out_tres_path, "w", encoding="utf-8") as f:
		f.write("\n".join(lines))


def write_spriteframes_npcs(
	png_path: str,
	out_paths_and_uids: List[Tuple[str, str]],
	frame_size: int = 256,
) -> None:
	"""
	NPC sheet layout (based on your sheet):
	- 3 NPCs across
	- Each NPC occupies 2 columns (2 frames per anim)
	- Rows:
	  0 = walk_down/front
	  1 = walk_up/back
	  2 = walk_right/side
	"""
	for npc_idx, (out_path, frames_uid) in enumerate(out_paths_and_uids):
		start_col = npc_idx * 2
		frames_per_anim = 2
		sub_count = 1 + 3 * frames_per_anim + frames_per_anim
		load_steps = 2 + sub_count

		lines: List[str] = []
		lines += [f'[gd_resource type="SpriteFrames" load_steps={load_steps} format=3 uid="{frames_uid}"]', ""]
		lines += [
			f'[ext_resource type="Texture2D" path="{_rel_res(png_path)}" id="1_texture"]',
			"",
		]

		sub_blocks: List[str] = []

		def add_atlas(id_name: str, x: int, y: int, flip_h: bool = False) -> str:
			block = [
				f'[sub_resource type="AtlasTexture" id="{id_name}"]',
				'atlas = ExtResource("1_texture")',
				f"region = Rect2({x}, {y}, {frame_size}, {frame_size})",
			]
			if flip_h:
				block.append("flip_h = true")
			sub_blocks.append("\n".join(block))
			return id_name

		idle_id = add_atlas("at_idle", start_col * frame_size, 0 * frame_size)

		def frames_for_row(prefix: str, row: int) -> List[str]:
			y = row * frame_size
			ids: List[str] = []
			for c in range(frames_per_anim):
				ids.append(add_atlas("%s_%d" % (prefix, c), (start_col + c) * frame_size, y, flip_h=False))
			return ids

		down = frames_for_row("at_down", 0)
		up = frames_for_row("at_up", 1)
		right = frames_for_row("at_right", 2)
		left: List[str] = []
		for c in range(frames_per_anim):
			left.append(add_atlas("at_left_%d" % c, (start_col + c) * frame_size, 2 * frame_size, flip_h=True))

		for i, block in enumerate(sub_blocks):
			if i > 0:
				lines.append("")
			lines.append(block)

		lines += ["", "[resource]", "animations = {"]
		lines += [
			'"idle": {',
			f'"frames": [SubResource("{idle_id}")],',
			'"loop": true,',
			'"speed": 2.0',
			"},",
		]

		def anim_block(name: str, ids: List[str]) -> List[str]:
			var_frames = ", ".join([f'SubResource("{i}")' for i in ids])
			return [
				f'"{name}": {{',
				f'"frames": [{var_frames}],',
				'"loop": true,',
				'"speed": 6.0',
				"},",
			]

		lines += anim_block("walk_down", down)
		lines += anim_block("walk_up", up)
		lines += anim_block("walk_right", right)
		lines += anim_block("walk_left", left)
		lines += ["}"]

		with open(out_path, "w", encoding="utf-8") as f:
			f.write("\n".join(lines))


def write_atlas_texture(
	out_path: str,
	uid: str,
	texture_uid: str,
	texture_res_path: str,
	region: Tuple[int, int, int, int],
) -> None:
	x, y, w, h = region
	lines = [
		f'[gd_resource type="AtlasTexture" load_steps=2 format=3 uid="{uid}"]',
		"",
		f'[ext_resource type="Texture2D" uid="{texture_uid}" path="{texture_res_path}" id="1_tex"]',
		"",
		"[resource]",
		'atlas = ExtResource("1_tex")',
		f"region = Rect2({x}, {y}, {w}, {h})",
	]
	os.makedirs(os.path.dirname(out_path), exist_ok=True)
	with open(out_path, "w", encoding="utf-8") as f:
		f.write("\n".join(lines))


def main() -> None:
	# 2) Tilesets (32x32)
	write_tileset(
		os.path.join(PROJECT_ROOT, "assets/tilesets/interior/interior_tileset.png"),
		os.path.join(PROJECT_ROOT, "assets/_imported/interior_tileset.tres"),
		tileset_uid="uid://qd3slad5x2k3",
		tile_size=32,
	)
	write_tileset(
		os.path.join(PROJECT_ROOT, "assets/tilesets/exterior/exterior_tileset.png"),
		os.path.join(PROJECT_ROOT, "assets/_imported/exterior_tileset.tres"),
		tileset_uid="uid://b385bcauwog0h",
		tile_size=32,
	)

	# 3) Player SpriteFrames (256px frames, 4 columns used, rows 0/1/2)
	write_spriteframes_player(
		os.path.join(PROJECT_ROOT, "assets/characters/player/player_character_wizard.png"),
		os.path.join(PROJECT_ROOT, "assets/_imported/player_frames.tres"),
		frames_uid="uid://mg0soy5bnyun",
		frame_size=256,
		cols_used=4,
		start_col=0,
		start_row=0,
	)

	# 4) NPC SpriteFrames (3 NPCs, 2 columns each, 256px frames)
	write_spriteframes_npcs(
		os.path.join(PROJECT_ROOT, "assets/characters/npcs/npc_sprites.png"),
		out_paths_and_uids=[
			(os.path.join(PROJECT_ROOT, "assets/_imported/npc1_frames.tres"), "uid://b34fnliuo7eqq"),
			(os.path.join(PROJECT_ROOT, "assets/_imported/npc2_frames.tres"), "uid://b34gnliuo7eqr"),
			(os.path.join(PROJECT_ROOT, "assets/_imported/npc3_frames.tres"), "uid://b34hnliuo7eqs"),
		],
		frame_size=256,
	)

	# 5) Chess pieces (assume 256px cells, 6 columns, 2 rows: white then black)
	pieces_png = os.path.join(PROJECT_ROOT, "assets/chess/pieces/chess_pieces.png")
	pieces_tex_uid = _get_texture_uid(pieces_png + ".import") or ""
	pieces_res = "res://assets/chess/pieces/chess_pieces.png"
	cell = 256
	# Column order in the sheet image appears: king, queen, knight, rook, pawn, (bishop slot or spare)
	order = ["king", "queen", "knight", "rook", "pawn", "bishop"]
	piece_code = {"king": "k", "queen": "q", "rook": "r", "bishop": "b", "knight": "n", "pawn": "p"}
	for row, color in enumerate(["white", "black"]):
		for col, piece in enumerate(order):
			out = os.path.join(PROJECT_ROOT, f"assets/_imported/chess_pieces/{color}_{piece}.tres")
			uid = f"uid://chess_{color[0]}{piece_code[piece]}002"
			write_atlas_texture(
				out_path=out,
				uid=uid,
				texture_uid=pieces_tex_uid,
				texture_res_path=pieces_res,
				region=(col * cell, row * cell, cell, cell),
			)

	# 6) UI kit (start with sane manual regions based on visible layout)
	# These can be refined further, but this gets ValidateUI showing properly without cutoffs.
	ui_png = os.path.join(PROJECT_ROOT, "assets/ui/ui_kit.png")
	ui_tex_uid = _get_texture_uid(ui_png + ".import") or ""
	ui_res = "res://assets/ui/ui_kit.png"

	ui_map: Dict[str, Tuple[str, Tuple[int, int, int, int]]] = {
		"assets/_imported/ui/panels/dialogue_panel.tres": ("uid://ui_dialogue001", (0, 0, 900, 300)),
		"assets/_imported/ui/panels/menu_panel.tres": ("uid://ui_menu001", (930, 0, 600, 300)),
		"assets/_imported/ui/panels/info_panel.tres": ("uid://ui_info001", (0, 520, 520, 360)),
		"assets/_imported/ui/buttons/button_normal.tres": ("uid://ui_btn_norm001", (200, 360, 420, 120)),
		"assets/_imported/ui/buttons/button_hover.tres": ("uid://ui_btn_hov001", (640, 360, 420, 120)),
		"assets/_imported/ui/buttons/button_pressed.tres": ("uid://ui_btn_prs001", (640, 520, 420, 120)),
		"assets/_imported/ui/icons/icon_chess.tres": ("uid://ui_icon_chs001", (0, 520, 420, 360)),
		"assets/_imported/ui/icons/icon_inventory.tres": ("uid://ui_icon_inv001", (1120, 640, 140, 140)),
		"assets/_imported/ui/icons/icon_settings.tres": ("uid://ui_icon_set001", (1280, 620, 160, 160)),
	}

	for out_path, (uid, region) in ui_map.items():
		write_atlas_texture(
			out_path=os.path.join(PROJECT_ROOT, out_path),
			uid=uid,
			texture_uid=ui_tex_uid,
			texture_res_path=ui_res,
			region=region,
		)

	print("\nPrepared assets + regenerated resources.")


if __name__ == "__main__":
	main()

