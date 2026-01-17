#!/usr/bin/env python3
"""
Fix SpriteFrames format to use numeric SubResource indices instead of string IDs.
"""

import os
import re

def fix_spriteframes_file(filepath):
    """Fix SubResource references to use numeric indices."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find all sub_resource definitions and map them to indices
    sub_resources = []
    lines = content.split('\n')
    
    # First pass: find all sub_resources and assign indices
    sub_resource_map = {}  # maps id to index
    current_index = 1  # Start from 1 (0 is reserved for ExtResource)
    
    for i, line in enumerate(lines):
        if line.startswith('[sub_resource'):
            # Extract the id
            match = re.search(r'id="([^"]+)"', line)
            if match:
                sub_id = match.group(1)
                sub_resource_map[sub_id] = current_index
                current_index += 1
    
    # Second pass: replace SubResource("id") with SubResource(index)
    new_lines = []
    for line in lines:
        # Replace SubResource("id") with SubResource(index)
        # Handle both SubResource("id") and SubResource("id") formats
        for sub_id, index in sub_resource_map.items():
            line = line.replace(f'SubResource("{sub_id}")', f'SubResource({index})')
        new_lines.append(line)
    
    # Write back
    with open(filepath, 'w') as f:
        f.write('\n'.join(new_lines))
    
    print(f"Fixed {filepath}: {len(sub_resource_map)} sub-resources mapped")

if __name__ == '__main__':
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    spriteframes_files = [
        os.path.join(project_root, 'assets', '_imported', 'player_frames.tres'),
        os.path.join(project_root, 'assets', '_imported', 'npc1_frames.tres'),
        os.path.join(project_root, 'assets', '_imported', 'npc2_frames.tres'),
        os.path.join(project_root, 'assets', '_imported', 'npc3_frames.tres'),
    ]
    
    for filepath in spriteframes_files:
        if os.path.exists(filepath):
            fix_spriteframes_file(filepath)
