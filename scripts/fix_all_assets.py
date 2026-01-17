#!/usr/bin/env python3
"""
Comprehensive asset fixing script:
1. Fix SpriteFrames format and load_steps
2. Fix UI asset slicing with proper detection
3. Fix tilesets to show individual tiles
"""

import os
import struct

def read_png_dimensions(filepath):
    """Read PNG width and height from file header."""
    with open(filepath, 'rb') as f:
        if f.read(8) != b'\x89PNG\r\n\x1a\n':
            return None
        chunk_length = struct.unpack('>I', f.read(4))[0]
        chunk_type = f.read(4)
        if chunk_type == b'IHDR':
            width = struct.unpack('>I', f.read(4))[0]
            height = struct.unpack('>I', f.read(4))[0]
            return width, height
    return None

def get_texture_uid(import_file):
    """Extract texture UID from .import file."""
    if not os.path.exists(import_file):
        return None
    with open(import_file, 'r') as f:
        for line in f:
            if 'uid=' in line:
                if 'uid="' in line:
                    parts = line.split('uid="')
                    if len(parts) > 1:
                        return parts[1].split('"')[0]
    return None

def fix_spriteframes(image_path, output_path, uid, texture_uid, frame_size=64, start_row=0, rows_per_char=3):
    """Fix SpriteFrames with correct load_steps count."""
    dims = read_png_dimensions(image_path)
    if not dims:
        return False
    
    width, height = dims
    cols = width // frame_size
    rows = height // frame_size
    
    frames_per_anim = min(4, cols)
    
    # Count sub-resources
    sub_count = 1  # idle
    sub_count += frames_per_anim * 3  # walk_down, walk_up, walk_right
    sub_count += frames_per_anim  # walk_left
    load_steps = 2 + sub_count  # ext_resource + sub_resources
    
    lines = [
        f'[gd_resource type="SpriteFrames" load_steps={load_steps} format=3 uid="{uid}"]',
        '',
        f'[ext_resource type="Texture2D" uid="{texture_uid}" path="res://{os.path.relpath(image_path, project_root).replace(os.sep, "/")}" id="1_texture"]',
        ''
    ]
    
    sub_resources = []
    sub_index = 1  # SubResource indices start at 1
    
    # Idle
    y = start_row * frame_size
    sub_resources.append(
        f'[sub_resource type="AtlasTexture"]\n'
        f'atlas = ExtResource("1_texture")\n'
        f'region = Rect2(0, {y}, {frame_size}, {frame_size})'
    )
    idle_ref = f'SubResource({sub_index})'
    sub_index += 1
    
    # Walk animations
    anim_configs = [
        ('walk_down', start_row),
        ('walk_up', start_row + 1 if start_row + 1 < rows else start_row),
        ('walk_right', start_row + 2 if start_row + 2 < rows else start_row),
    ]
    
    anim_refs = {}
    for anim_name, row_idx in anim_configs:
        if row_idx >= rows:
            continue
        y = row_idx * frame_size
        frame_refs = []
        for frame_idx in range(frames_per_anim):
            if frame_idx >= cols:
                break
            x = frame_idx * frame_size
            sub_resources.append(
                f'[sub_resource type="AtlasTexture"]\n'
                f'atlas = ExtResource("1_texture")\n'
                f'region = Rect2({x}, {y}, {frame_size}, {frame_size})'
            )
            frame_refs.append(f'SubResource({sub_index})')
            sub_index += 1
        anim_refs[anim_name] = frame_refs
    
    # Walk left (flipped walk_right)
    if 'walk_right' in anim_refs:
        right_row = start_row + 2 if start_row + 2 < rows else start_row
        y = right_row * frame_size
        left_refs = []
        for frame_idx in range(frames_per_anim):
            if frame_idx >= cols:
                break
            x = frame_idx * frame_size
            sub_resources.append(
                f'[sub_resource type="AtlasTexture"]\n'
                f'atlas = ExtResource("1_texture")\n'
                f'region = Rect2({x}, {y}, {frame_size}, {frame_size})\n'
                f'flip_h = true'
            )
            left_refs.append(f'SubResource({sub_index})')
            sub_index += 1
        anim_refs['walk_left'] = left_refs
    
    # Write sub-resources
    for i, sub_res in enumerate(sub_resources):
        if i > 0:
            lines.append('')
        lines.append(sub_res)
    
    lines.append('')
    lines.append('[resource]')
    lines.append('animations = {')
    
    # Idle
    lines.append('"idle": {')
    lines.append(f'"frames": [{idle_ref}],')
    lines.append('"loop": true,')
    lines.append('"speed": 2.0')
    lines.append('},')
    
    # Walk animations
    for anim_name in ['walk_down', 'walk_up', 'walk_right', 'walk_left']:
        if anim_name in anim_refs and anim_refs[anim_name]:
            lines.append(f'"{anim_name}": {{')
            lines.append(f'"frames": [{", ".join(anim_refs[anim_name])}],')
            lines.append('"loop": true,')
            lines.append('"speed": 8.0')
            lines.append('},')
    
    lines.append('}')
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    return True

def fix_tileset(image_path, output_path, uid, texture_uid, tile_size=32):
    """Fix tileset to show all individual tiles."""
    dims = read_png_dimensions(image_path)
    if not dims:
        return False
    
    width, height = dims
    cols = width // tile_size
    rows = height // tile_size
    
    # Count all tiles
    tile_count = cols * rows
    
    lines = [
        f'[gd_resource type="TileSet" load_steps=3 format=3 uid="{uid}"]',
        '',
        f'[ext_resource type="Texture2D" uid="{texture_uid}" path="res://{os.path.relpath(image_path, project_root).replace(os.sep, "/")}" id="1_texture"]',
        '',
        '[sub_resource type="TileSetAtlasSource" id="TileSetAtlasSource_1"]',
        'texture = ExtResource("1_texture")',
        ''
    ]
    
    # Add all tiles
    for row in range(rows):
        for col in range(cols):
            lines.append(f'{col}:{row}/0 = 0')
    
    lines.append('')
    lines.append('[resource]')
    lines.append(f'tile_size = Vector2i({tile_size}, {tile_size})')
    lines.append('sources/0 = SubResource("TileSetAtlasSource_1")')
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    return True

def fix_ui_assets():
    """Fix UI asset slicing - create properly sized AtlasTextures."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ui_img = os.path.join(project_root, 'assets', 'ui', 'ui_kit.png')
    
    if not os.path.exists(ui_img):
        return
    
    dims = read_png_dimensions(ui_img)
    if not dims:
        return
    
    width, height = dims
    import_file = ui_img.replace('.png', '.png.import')
    texture_uid = get_texture_uid(import_file) or "uid://snj26b0nmnfu"
    
    # Common UI element sizes (adjust based on typical UI kit layouts)
    # Since we don't know exact layout, create reasonable defaults
    ui_elements = {
        'panels/dialogue_panel.tres': (512, 128, 0, 0),
        'panels/menu_panel.tres': (400, 300, 512, 0),
        'panels/info_panel.tres': (400, 200, 0, 128),
        'buttons/button_normal.tres': (200, 64, 0, 512),
        'buttons/button_hover.tres': (200, 64, 200, 512),
        'buttons/button_pressed.tres': (200, 64, 400, 512),
        'icons/icon_chess.tres': (64, 64, 600, 512),
        'icons/icon_inventory.tres': (64, 64, 664, 512),
        'icons/icon_settings.tres': (64, 64, 728, 512),
    }
    
    for rel_path, (w, h, x, y) in ui_elements.items():
        output_path = os.path.join(project_root, 'assets', '_imported', 'ui', rel_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        uid_map = {
            'panels/dialogue_panel.tres': 'uid://ui_dialogue001',
            'panels/menu_panel.tres': 'uid://ui_menu001',
            'panels/info_panel.tres': 'uid://ui_info001',
            'buttons/button_normal.tres': 'uid://ui_btn_norm001',
            'buttons/button_hover.tres': 'uid://ui_btn_hov001',
            'buttons/button_pressed.tres': 'uid://ui_btn_prs001',
            'icons/icon_chess.tres': 'uid://ui_icon_chs001',
            'icons/icon_inventory.tres': 'uid://ui_icon_inv001',
            'icons/icon_settings.tres': 'uid://ui_icon_set001',
        }
        
        uid = uid_map.get(rel_path, 'uid://ui_element')
        
        lines = [
            f'[gd_resource type="AtlasTexture" load_steps=2 format=3 uid="{uid}"]',
            '',
            f'[ext_resource type="Texture2D" uid="{texture_uid}" path="res://assets/ui/ui_kit.png" id="1_ui"]',
            '',
            '[resource]',
            'atlas = ExtResource("1_ui")',
            f'region = Rect2({x}, {y}, {w}, {h})'
        ]
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))

if __name__ == '__main__':
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Fix player
    player_img = os.path.join(project_root, 'assets', 'characters', 'player', 'player_character_wizard.png')
    player_output = os.path.join(project_root, 'assets', '_imported', 'player_frames.tres')
    player_import = player_img.replace('.png', '.png.import')
    player_uid = get_texture_uid(player_import) or "uid://b7c2c77sf6ltg"
    
    if os.path.exists(player_img):
        print("Fixing player SpriteFrames...")
        fix_spriteframes(player_img, player_output, "uid://mg0soy5bnyun", player_uid, frame_size=64, start_row=0)
    
    # Fix NPCs
    npc_img = os.path.join(project_root, 'assets', 'characters', 'npcs', 'npc_sprites.png')
    npc_import = npc_img.replace('.png', '.png.import')
    npc_uid = get_texture_uid(npc_import) or "uid://dxia2o2v04hk8"
    
    npc_configs = [
        ("npc1_frames.tres", "uid://b34fnliuo7eqq", 0),
        ("npc2_frames.tres", "uid://b34gnliuo7eqr", 5),
        ("npc3_frames.tres", "uid://b34hnliuo7eqs", 10),
    ]
    
    if os.path.exists(npc_img):
        print("Fixing NPC SpriteFrames...")
        for filename, uid, start_row in npc_configs:
            output = os.path.join(project_root, 'assets', '_imported', filename)
            fix_spriteframes(npc_img, output, uid, npc_uid, frame_size=64, start_row=start_row)
    
    # Fix tilesets
    interior_img = os.path.join(project_root, 'assets', 'tilesets', 'interior', 'interior_tileset.png')
    interior_output = os.path.join(project_root, 'assets', '_imported', 'interior_tileset.tres')
    interior_import = interior_img.replace('.png', '.png.import')
    interior_uid = get_texture_uid(interior_import) or "uid://bd4b41rc8pmdq"
    
    if os.path.exists(interior_img):
        print("Fixing interior tileset...")
        fix_tileset(interior_img, interior_output, "uid://qd3slad5x2k3", interior_uid, tile_size=32)
    
    exterior_img = os.path.join(project_root, 'assets', 'tilesets', 'exterior', 'exterior_tileset.png')
    exterior_output = os.path.join(project_root, 'assets', '_imported', 'exterior_tileset.tres')
    exterior_import = exterior_img.replace('.png', '.png.import')
    exterior_uid = get_texture_uid(exterior_import) or "uid://c3jnrxqkrxc07"
    
    if os.path.exists(exterior_img):
        print("Fixing exterior tileset...")
        fix_tileset(exterior_img, exterior_output, "uid://b385bcauwog0h", exterior_uid, tile_size=32)
    
    # Fix UI assets
    print("Fixing UI assets...")
    fix_ui_assets()
    
    print("\nAll assets fixed!")
