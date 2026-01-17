#!/usr/bin/env python3
"""
Simple sprite sheet analyzer using basic image analysis.
Falls back to reasonable defaults if analysis fails.
"""

import sys
import os
import struct

def read_png_dimensions(filepath):
    """Read PNG width and height from file header."""
    with open(filepath, 'rb') as f:
        # PNG signature
        if f.read(8) != b'\x89PNG\r\n\x1a\n':
            return None
        
        # Read first IHDR chunk
        chunk_length = struct.unpack('>I', f.read(4))[0]
        chunk_type = f.read(4)
        
        if chunk_type == b'IHDR':
            width = struct.unpack('>I', f.read(4))[0]
            height = struct.unpack('>I', f.read(4))[0]
            return width, height
    
    return None

def detect_frame_size_from_dimensions(width, height, preferred_size=None):
    """Detect likely frame size from image dimensions."""
    # If preferred size is given and works, use it
    if preferred_size and width % preferred_size == 0 and height % preferred_size == 0:
        return preferred_size
    
    # Common frame sizes (prefer larger sizes first)
    common_sizes = [128, 96, 64, 48, 32]
    
    for size in common_sizes:
        if width % size == 0 and height % size == 0:
            cols = width // size
            rows = height // size
            # Prefer sizes that give reasonable grid
            if cols >= 3 and rows >= 3:
                return size
    
    # Default to 64 if no good match
    return 64

def get_texture_uid(import_file):
    """Extract texture UID from .import file."""
    if not os.path.exists(import_file):
        return None
    
    with open(import_file, 'r') as f:
        for line in f:
            if 'uid=' in line:
                # Try to extract UID
                if 'uid="' in line:
                    parts = line.split('uid="')
                    if len(parts) > 1:
                        return parts[1].split('"')[0]
                elif 'uid=' in line:
                    parts = line.split('uid=')
                    if len(parts) > 1:
                        uid_part = parts[1].strip().strip('"').strip("'")
                        if uid_part.startswith('uid://'):
                            return uid_part
    
    return None

def generate_player_spriteframes(image_path, output_path):
    """Generate player SpriteFrames with detected layout."""
    dims = read_png_dimensions(image_path)
    if not dims:
        print(f"Could not read dimensions from {image_path}")
        return
    
    width, height = dims
    # Characters should be 64x64 per user specification
    frame_size = 64  # Force 64x64 for characters
    if width % frame_size != 0 or height % frame_size != 0:
        # Fallback if 64 doesn't work
        frame_size = detect_frame_size_from_dimensions(width, height)
    cols = width // frame_size
    rows = height // frame_size
    
    print(f"Player sprite sheet: {width}x{height}")
    print(f"Detected frame size: {frame_size}x{frame_size}")
    print(f"Grid: {cols} columns x {rows} rows")
    
    # Get texture UID
    import_file = image_path.replace('.png', '.png.import')
    texture_uid = get_texture_uid(import_file) or "uid://b7c2c77sf6ltg"
    
    # Assume animations are in rows: row 0 = walk_down, row 1 = walk_up, row 2 = walk_right
    # Assume 4 frames per animation (common pattern)
    frames_per_anim = min(4, cols)
    
    lines = [
        f'[gd_resource type="SpriteFrames" load_steps=2 format=3 uid="uid://mg0soy5bnyun"]',
        '',
        f'[ext_resource type="Texture2D" uid="{texture_uid}" path="res://assets/characters/player/player_character_wizard.png" id="1_player"]',
        ''
    ]
    
    sub_resources = []
    
    # Idle (first frame of walk_down)
    sub_resources.append(
        '[sub_resource type="AtlasTexture" id="AtlasTexture_idle"]\n'
        f'atlas = ExtResource("1_player")\n'
        f'region = Rect2(0, 0, {frame_size}, {frame_size})'
    )
    
    # Walk animations
    anim_configs = [
        ('walk_down', 0),
        ('walk_up', 1 if rows > 1 else 0),
        ('walk_right', 2 if rows > 2 else 0),
    ]
    
    for anim_name, row_idx in anim_configs:
        if row_idx >= rows:
            continue
        
        y = row_idx * frame_size
        for frame_idx in range(frames_per_anim):
            if frame_idx >= cols:
                break
            x = frame_idx * frame_size
            sub_id = f'AtlasTexture_{anim_name}_{frame_idx}'
            sub_resources.append(
                f'[sub_resource type="AtlasTexture" id="{sub_id}"]\n'
                f'atlas = ExtResource("1_player")\n'
                f'region = Rect2({x}, {y}, {frame_size}, {frame_size})'
            )
    
    # Walk left (flipped walk_right)
    if rows > 2:
        y = 2 * frame_size
        for frame_idx in range(frames_per_anim):
            if frame_idx >= cols:
                break
            x = frame_idx * frame_size
            sub_id = f'AtlasTexture_walk_left_{frame_idx}'
            sub_resources.append(
                f'[sub_resource type="AtlasTexture" id="{sub_id}"]\n'
                f'atlas = ExtResource("1_player")\n'
                f'region = Rect2({x}, {y}, {frame_size}, {frame_size})\n'
                f'flip_h = true'
            )
    
    # Add sub-resources with proper spacing
    for i, sub_res in enumerate(sub_resources):
        if i > 0:
            lines.append('')
        lines.append(sub_res)
    
    lines.append('')
    lines.append('[resource]')
    lines.append('animations = {')
    
    # Idle
    lines.append('"idle": {')
    lines.append('"frames": [SubResource("AtlasTexture_idle")],')
    lines.append('"loop": true,')
    lines.append('"speed": 2.0')
    lines.append('},')
    
    # Walk animations
    for anim_name, row_idx in anim_configs:
        if row_idx >= rows:
            continue
        frame_refs = [f'SubResource("AtlasTexture_{anim_name}_{i}")' for i in range(frames_per_anim) if i < cols]
        if frame_refs:
            lines.append(f'"{anim_name}": {{')
            lines.append(f'"frames": [{", ".join(frame_refs)}],')
            lines.append('"loop": true,')
            lines.append('"speed": 8.0')
            lines.append('},')
    
    # Walk left
    if rows > 2:
        frame_refs = [f'SubResource("AtlasTexture_walk_left_{i}")' for i in range(frames_per_anim) if i < cols]
        if frame_refs:
            lines.append('"walk_left": {')
            lines.append(f'"frames": [{", ".join(frame_refs)}],')
            lines.append('"loop": true,')
            lines.append('"speed": 8.0')
            lines.append('},')
    
    lines.append('}')
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"Generated: {output_path}")

def generate_npc_spriteframes(image_path, output_paths, npc_count=3):
    """Generate NPC SpriteFrames."""
    dims = read_png_dimensions(image_path)
    if not dims:
        print(f"Could not read dimensions from {image_path}")
        return
    
    width, height = dims
    # Characters should be 64x64 per user specification
    frame_size = 64  # Force 64x64 for characters
    if width % frame_size != 0 or height % frame_size != 0:
        # Fallback if 64 doesn't work
        frame_size = detect_frame_size_from_dimensions(width, height)
    cols = width // frame_size
    rows = height // frame_size
    
    print(f"\nNPC sprite sheet: {width}x{height}")
    print(f"Detected frame size: {frame_size}x{frame_size}")
    print(f"Grid: {cols} columns x {rows} rows")
    
    # Get texture UID
    import_file = image_path.replace('.png', '.png.import')
    texture_uid = get_texture_uid(import_file) or "uid://dxia2o2v04hk8"
    
    # Determine NPC layout
    # Assume NPCs are arranged: each NPC gets rows_per_npc rows
    rows_per_npc = max(1, rows // npc_count)
    frames_per_anim = min(4, cols)
    
    uid_map = {
        0: "uid://b34fnliuo7eqq",
        1: "uid://b34gnliuo7eqr",
        2: "uid://b34hnliuo7eqs"
    }
    
    for npc_idx in range(npc_count):
        npc_start_row = npc_idx * rows_per_npc
        output_path = output_paths[npc_idx]
        
        lines = [
            f'[gd_resource type="SpriteFrames" load_steps=2 format=3 uid="{uid_map.get(npc_idx, "uid://npc_frames")}"]',
            '',
            f'[ext_resource type="Texture2D" uid="{texture_uid}" path="res://assets/characters/npcs/npc_sprites.png" id="1_npcs"]',
            ''
        ]
        
        sub_resources = []
        
        # Idle (first frame of first animation row for this NPC)
        idle_row = npc_start_row
        idle_col = 0
        if idle_row < rows:
            sub_resources.append(
                '[sub_resource type="AtlasTexture" id="AtlasTexture_idle"]\n'
                f'atlas = ExtResource("1_npcs")\n'
                f'region = Rect2({idle_col * frame_size}, {idle_row * frame_size}, {frame_size}, {frame_size})'
            )
        
        # Walk animations (assume 3 rows per NPC: down, up, right)
        anim_configs = [
            ('walk_down', npc_start_row),
            ('walk_up', npc_start_row + 1 if npc_start_row + 1 < rows else npc_start_row),
            ('walk_right', npc_start_row + 2 if npc_start_row + 2 < rows else npc_start_row),
        ]
        
        for anim_name, row_idx in anim_configs:
            if row_idx >= rows:
                continue
            y = row_idx * frame_size
            for frame_idx in range(frames_per_anim):
                if frame_idx >= cols:
                    break
                x = frame_idx * frame_size
                sub_id = f'AtlasTexture_{anim_name}_{frame_idx}'
                sub_resources.append(
                    f'[sub_resource type="AtlasTexture" id="{sub_id}"]\n'
                    f'atlas = ExtResource("1_npcs")\n'
                    f'region = Rect2({x}, {y}, {frame_size}, {frame_size})'
                )
        
        # Walk left (flipped walk_right)
        right_row = npc_start_row + 2 if npc_start_row + 2 < rows else npc_start_row
        if right_row < rows:
            y = right_row * frame_size
            for frame_idx in range(frames_per_anim):
                if frame_idx >= cols:
                    break
                x = frame_idx * frame_size
                sub_id = f'AtlasTexture_walk_left_{frame_idx}'
                sub_resources.append(
                    f'[sub_resource type="AtlasTexture" id="{sub_id}"]\n'
                    f'atlas = ExtResource("1_npcs")\n'
                    f'region = Rect2({x}, {y}, {frame_size}, {frame_size})\n'
                    f'flip_h = true'
                )
        
        lines.extend(sub_resources)
        lines.append('')
        lines.append('[resource]')
        lines.append('animations = {')
        
        # Idle
        if idle_row < rows:
            lines.append('"idle": {')
            lines.append('"frames": [SubResource("AtlasTexture_idle")],')
            lines.append('"loop": true,')
            lines.append('"speed": 2.0')
            lines.append('},')
        
        # Walk animations
        for anim_name, row_idx in anim_configs:
            if row_idx >= rows:
                continue
            frame_refs = [f'SubResource("AtlasTexture_{anim_name}_{i}")' for i in range(frames_per_anim) if i < cols]
            if frame_refs:
                lines.append(f'"{anim_name}": {{')
                lines.append(f'"frames": [{", ".join(frame_refs)}],')
                lines.append('"loop": true,')
                lines.append('"speed": 8.0')
                lines.append('},')
        
        # Walk left
        if right_row < rows:
            frame_refs = [f'SubResource("AtlasTexture_walk_left_{i}")' for i in range(frames_per_anim) if i < cols]
            if frame_refs:
                lines.append('"walk_left": {')
                lines.append(f'"frames": [{", ".join(frame_refs)}],')
                lines.append('"loop": true,')
                lines.append('"speed": 8.0')
                lines.append('},')
        
        lines.append('}')
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"Generated NPC {npc_idx + 1}: {output_path}")

if __name__ == '__main__':
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Player sprite
    player_img = os.path.join(project_root, 'assets', 'characters', 'player', 'player_character_wizard.png')
    player_output = os.path.join(project_root, 'assets', '_imported', 'player_frames.tres')
    
    if os.path.exists(player_img):
        print("Analyzing player sprite sheet...")
        generate_player_spriteframes(player_img, player_output)
    else:
        print(f"Player sprite not found: {player_img}")
    
    # NPC sprites
    npc_img = os.path.join(project_root, 'assets', 'characters', 'npcs', 'npc_sprites.png')
    npc_outputs = [
        os.path.join(project_root, 'assets', '_imported', 'npc1_frames.tres'),
        os.path.join(project_root, 'assets', '_imported', 'npc2_frames.tres'),
        os.path.join(project_root, 'assets', '_imported', 'npc3_frames.tres'),
    ]
    
    if os.path.exists(npc_img):
        print("\nAnalyzing NPC sprite sheet...")
        generate_npc_spriteframes(npc_img, npc_outputs, npc_count=3)
    else:
        print(f"NPC sprite not found: {npc_img}")
