#!/usr/bin/env python3
"""
Analyze sprite sheets and auto-detect frame layouts for Godot SpriteFrames.
"""

import sys
import os
from PIL import Image
import numpy as np

def detect_frame_size(image_path):
    """Detect frame size by looking for repeating patterns."""
    img = Image.open(image_path)
    width, height = img.size
    
    # Convert to numpy array for analysis
    img_array = np.array(img)
    
    # Try common frame sizes
    common_sizes = [32, 48, 64, 96, 128]
    
    best_size = None
    best_score = 0
    
    for size in common_sizes:
        if width % size == 0 and height % size == 0:
            # Check if frames are uniform by sampling edges
            score = 0
            cols = width // size
            rows = height // size
            
            # Sample corners of frames to see if they're consistent
            for r in range(min(rows, 3)):
                for c in range(min(cols, 3)):
                    x = c * size
                    y = r * size
                    # Check if frame has content (not all transparent/empty)
                    frame = img_array[y:y+size, x:x+size]
                    if len(frame.shape) == 3:
                        # Check alpha channel if exists
                        if frame.shape[2] == 4:
                            alpha = frame[:, :, 3]
                            if np.any(alpha > 0):
                                score += 1
                        else:
                            # No alpha, check if not all same color
                            if not np.all(frame == frame[0, 0]):
                                score += 1
            
            if score > best_score:
                best_score = score
                best_size = size
    
    return best_size if best_size else 64  # Default to 64

def detect_animations(image_path, frame_size):
    """Detect animation rows/columns."""
    img = Image.open(image_path)
    width, height = img.size
    
    cols = width // frame_size
    rows = height // frame_size
    
    # Analyze each row to see if it contains frames
    img_array = np.array(img)
    
    animation_rows = []
    for r in range(rows):
        row_frames = []
        for c in range(cols):
            x = c * frame_size
            y = r * frame_size
            frame = img_array[y:y+frame_size, x:x+frame_size]
            
            # Check if frame has content
            has_content = False
            if len(frame.shape) == 3:
                if frame.shape[2] == 4:  # RGBA
                    alpha = frame[:, :, 3]
                    has_content = np.any(alpha > 10)  # Threshold for transparency
                else:  # RGB
                    # Check if not all same color
                    has_content = not np.allclose(frame, frame[0, 0, :], atol=5)
            
            if has_content:
                row_frames.append(c)
        
        if row_frames:
            animation_rows.append({
                'row': r,
                'frames': sorted(row_frames),
                'frame_count': len(row_frames)
            })
    
    return animation_rows, cols, rows

def generate_player_spriteframes(image_path, output_path):
    """Generate player SpriteFrames resource."""
    frame_size = detect_frame_size(image_path)
    animations, cols, rows = detect_animations(image_path, frame_size)
    
    print(f"Detected frame size: {frame_size}x{frame_size}")
    print(f"Sprite sheet: {cols} columns x {rows} rows")
    print(f"Found {len(animations)} animation rows")
    
    # Get texture UID from import file
    import_file = image_path.replace('.png', '.png.import')
    texture_uid = None
    if os.path.exists(import_file):
        with open(import_file, 'r') as f:
            for line in f:
                if 'uid=' in line:
                    texture_uid = line.split('uid="')[1].split('"')[0]
                    break
    
    if not texture_uid:
        texture_uid = "uid://player_texture"
    
    # Generate SpriteFrames resource
    lines = [
        f'[gd_resource type="SpriteFrames" load_steps=2 format=3 uid="uid://mg0soy5bnyun"]',
        '',
        f'[ext_resource type="Texture2D" uid="{texture_uid}" path="res://assets/characters/player/player_character_wizard.png" id="1_player"]',
        ''
    ]
    
    sub_resources = []
    animation_defs = {}
    
    # Map detected rows to animation names
    anim_names = ['walk_down', 'walk_up', 'walk_right']
    for i, anim_row in enumerate(animations[:3]):  # First 3 rows
        anim_name = anim_names[i] if i < len(anim_names) else f"anim_{i}"
        frames = []
        
        for frame_idx, col in enumerate(anim_row['frames']):
            sub_id = f'AtlasTexture_{anim_name}_{frame_idx}'
            x = col * frame_size
            y = anim_row['row'] * frame_size
            
            sub_resources.append(
                f'[sub_resource type="AtlasTexture" id="{sub_id}"]\n'
                f'atlas = ExtResource("1_player")\n'
                f'region = Rect2({x}, {y}, {frame_size}, {frame_size})'
            )
            frames.append(f'SubResource("{sub_id}")')
        
        # Create idle from first frame
        idle_sub_id = f'AtlasTexture_idle'
        if idle_sub_id not in [s.split('id="')[1].split('"')[0] for s in sub_resources]:
            first_frame = anim_row['frames'][0]
            sub_resources.insert(0, 
                f'[sub_resource type="AtlasTexture" id="{idle_sub_id}"]\n'
                f'atlas = ExtResource("1_player")\n'
                f'region = Rect2({first_frame * frame_size}, {anim_row["row"] * frame_size}, {frame_size}, {frame_size})'
            )
        
        animation_defs[anim_name] = {
            'frames': frames,
            'loop': True,
            'speed': 8.0
        }
    
    # Add idle animation
    animation_defs['idle'] = {
        'frames': ['SubResource("AtlasTexture_idle")'],
        'loop': True,
        'speed': 2.0
    }
    
    # Add walk_left (flipped walk_right)
    if 'walk_right' in animation_defs:
        walk_right_frames = animation_defs['walk_right']['frames']
        left_frames = []
        for i, frame_ref in enumerate(walk_right_frames):
            sub_id = f'AtlasTexture_walk_left_{i}'
            # Extract region from walk_right frame
            right_sub = [s for s in sub_resources if f'walk_right_{i}' in s][0]
            region_line = [l for l in right_sub.split('\n') if 'region =' in l][0]
            region = region_line.split('Rect2(')[1].split(')')[0]
            
            sub_resources.append(
                f'[sub_resource type="AtlasTexture" id="{sub_id}"]\n'
                f'atlas = ExtResource("1_player")\n'
                f'region = Rect2({region})\n'
                f'flip_h = true'
            )
            left_frames.append(f'SubResource("{sub_id}")')
        
        animation_defs['walk_left'] = {
            'frames': left_frames,
            'loop': True,
            'speed': 8.0
        }
    
    # Write sub-resources
    lines.extend(sub_resources)
    lines.append('')
    lines.append('[resource]')
    lines.append('animations = {')
    
    # Write animations
    for anim_name, anim_data in animation_defs.items():
        lines.append(f'"{anim_name}": {{')
        lines.append(f'"frames": [{", ".join(anim_data["frames"])}],')
        lines.append(f'"loop": {str(anim_data["loop"]).lower()},')
        lines.append(f'"speed": {anim_data["speed"]}')
        lines.append('},')
    
    lines.append('}')
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"Generated: {output_path}")

def generate_npc_spriteframes(image_path, output_paths, npc_count=3):
    """Generate NPC SpriteFrames resources."""
    frame_size = detect_frame_size(image_path)
    animations, cols, rows = detect_animations(image_path, frame_size)
    
    print(f"\nNPC Sprite Sheet Analysis:")
    print(f"Detected frame size: {frame_size}x{frame_size}")
    print(f"Sprite sheet: {cols} columns x {rows} rows")
    print(f"Found {len(animations)} animation rows")
    
    # Get texture UID
    import_file = image_path.replace('.png', '.png.import')
    texture_uid = None
    if os.path.exists(import_file):
        with open(import_file, 'r') as f:
            for line in f:
                if 'uid=' in line:
                    texture_uid = line.split('uid="')[0].split('uid="')[1].split('"')[0] if 'uid="' in line else None
                    if not texture_uid:
                        parts = line.split('uid=')
                        if len(parts) > 1:
                            texture_uid = parts[1].split('"')[1] if '"' in parts[1] else parts[1].strip()
                    break
    
    if not texture_uid:
        texture_uid = "uid://npc_texture"
    
    # Determine NPC layout - assume each NPC takes a set of rows
    rows_per_npc = rows // npc_count if rows >= npc_count else 1
    
    for npc_idx in range(npc_count):
        npc_start_row = npc_idx * rows_per_npc
        npc_animations = [a for a in animations if npc_start_row <= a['row'] < npc_start_row + rows_per_npc]
        
        if not npc_animations:
            # Fallback: use all animations divided by NPC count
            anims_per_npc = len(animations) // npc_count
            npc_animations = animations[npc_idx * anims_per_npc:(npc_idx + 1) * anims_per_npc]
        
        output_path = output_paths[npc_idx]
        uid_map = {
            0: "uid://b34fnliuo7eqq",
            1: "uid://b34gnliuo7eqr",
            2: "uid://b34hnliuo7eqs"
        }
        
        lines = [
            f'[gd_resource type="SpriteFrames" load_steps=2 format=3 uid="{uid_map.get(npc_idx, "uid://npc_frames")}"]',
            '',
            f'[ext_resource type="Texture2D" uid="{texture_uid}" path="res://assets/characters/npcs/npc_sprites.png" id="1_npcs"]',
            ''
        ]
        
        sub_resources = []
        animation_defs = {}
        
        anim_names = ['walk_down', 'walk_up', 'walk_right']
        for i, anim_row in enumerate(npc_animations[:3]):
            anim_name = anim_names[i] if i < len(anim_names) else f"anim_{i}"
            frames = []
            
            for frame_idx, col in enumerate(anim_row['frames']):
                sub_id = f'AtlasTexture_{anim_name}_{frame_idx}'
                x = col * frame_size
                y = anim_row['row'] * frame_size
                
                sub_resources.append(
                    f'[sub_resource type="AtlasTexture" id="{sub_id}"]\n'
                    f'atlas = ExtResource("1_npcs")\n'
                    f'region = Rect2({x}, {y}, {frame_size}, {frame_size})'
                )
                frames.append(f'SubResource("{sub_id}")')
            
            animation_defs[anim_name] = {
                'frames': frames,
                'loop': True,
                'speed': 8.0
            }
        
        # Idle from first frame
        if npc_animations:
            first_anim = npc_animations[0]
            first_col = first_anim['frames'][0]
            idle_sub_id = 'AtlasTexture_idle'
            sub_resources.insert(0,
                f'[sub_resource type="AtlasTexture" id="{idle_sub_id}"]\n'
                f'atlas = ExtResource("1_npcs")\n'
                f'region = Rect2({first_col * frame_size}, {first_anim["row"] * frame_size}, {frame_size}, {frame_size})'
            )
            animation_defs['idle'] = {
                'frames': [f'SubResource("{idle_sub_id}")'],
                'loop': True,
                'speed': 2.0
            }
        
        # walk_left (flipped walk_right)
        if 'walk_right' in animation_defs:
            walk_right_frames = animation_defs['walk_right']['frames']
            left_frames = []
            for i, frame_ref in enumerate(walk_right_frames):
                sub_id = f'AtlasTexture_walk_left_{i}'
                right_sub = [s for s in sub_resources if f'walk_right_{i}' in s][0]
                region_line = [l for l in right_sub.split('\n') if 'region =' in l][0]
                region = region_line.split('Rect2(')[1].split(')')[0]
                
                sub_resources.append(
                    f'[sub_resource type="AtlasTexture" id="{sub_id}"]\n'
                    f'atlas = ExtResource("1_npcs")\n'
                    f'region = Rect2({region})\n'
                    f'flip_h = true'
                )
                left_frames.append(f'SubResource("{sub_id}")')
            
            animation_defs['walk_left'] = {
                'frames': left_frames,
                'loop': True,
                'speed': 8.0
            }
        
        lines.extend(sub_resources)
        lines.append('')
        lines.append('[resource]')
        lines.append('animations = {')
        
        for anim_name, anim_data in animation_defs.items():
            lines.append(f'"{anim_name}": {{')
            lines.append(f'"frames": [{", ".join(anim_data["frames"])}],')
            lines.append(f'"loop": {str(anim_data["loop"]).lower()},')
            lines.append(f'"speed": {anim_data["speed"]}')
            lines.append('},')
        
        lines.append('}')
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"Generated: {output_path}")

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
