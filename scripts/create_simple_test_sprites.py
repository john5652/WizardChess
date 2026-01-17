#!/usr/bin/env python3
"""
Create simple test sprites using basic Python (no PIL required).
Creates minimal PNG files with colored pixels for testing.
"""

import struct
import os

def create_simple_png(width, height, color_r=255, color_g=255, color_b=255, color_a=255):
    """Create a simple PNG with a solid color."""

    # PNG signature
    png_signature = b'\x89PNG\r\n\x1a\n'

    # IHDR chunk
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)  # 8-bit RGBA
    ihdr_crc = 0x9a7c8170  # Pre-calculated CRC for this IHDR
    ihdr_chunk = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)

    # IDAT chunk - simple solid color image data
    # For simplicity, create a 1x1 pixel and repeat it
    pixel_data = bytes([color_r, color_g, color_b, color_a])
    scanline = b'\x00' + pixel_data * width  # Filter byte + pixel data
    image_data = scanline * height

    # Compress with zlib (simple case)
    import zlib
    compressed_data = zlib.compress(image_data)

    idat_chunk = struct.pack('>I', len(compressed_data)) + b'IDAT' + compressed_data
    idat_crc = zlib.crc32(b'IDAT' + compressed_data) & 0xffffffff
    idat_chunk += struct.pack('>I', idat_crc)

    # IEND chunk
    iend_chunk = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', 0xae426082)

    return png_signature + ihdr_chunk + idat_chunk + iend_chunk

def create_test_sprite_sheet():
    """Create a simple sprite sheet with different colored squares."""
    # Create a 256x256 image with 4x4 grid of colored squares
    width, height = 256, 256
    square_size = 64  # 64x64 squares

    # Create base image data
    pixels = []
    colors = [
        (255, 0, 0, 255),     # Red
        (0, 255, 0, 255),     # Green
        (0, 0, 255, 255),     # Blue
        (255, 255, 0, 255),   # Yellow
        (255, 0, 255, 255),   # Magenta
        (0, 255, 255, 255),   # Cyan
        (255, 128, 0, 255),   # Orange
        (128, 0, 255, 255),   # Purple
        (128, 128, 128, 255), # Gray
        (0, 128, 0, 255),     # Dark Green
        (0, 0, 128, 255),     # Dark Blue
        (128, 0, 0, 255),     # Dark Red
        (255, 255, 255, 255), # White
        (0, 0, 0, 255),       # Black
        (192, 192, 192, 255), # Light Gray
        (64, 64, 64, 255),    # Dark Gray
    ]

    for y in range(height):
        for x in range(width):
            square_x = x // square_size
            square_y = y // square_size
            color_index = (square_y * 4 + square_x) % len(colors)
            r, g, b, a = colors[color_index]
            pixels.extend([r, g, b, a])

    # Convert to bytes
    image_data = bytes(pixels)

    # Create PNG
    png_signature = b'\x89PNG\r\n\x1a\n'

    # IHDR chunk
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)  # 8-bit RGBA
    ihdr_crc = 0x9a7c8170  # Pre-calculated CRC
    ihdr_chunk = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)

    # IDAT chunk
    import zlib
    compressed_data = zlib.compress(image_data)

    idat_chunk = struct.pack('>I', len(compressed_data)) + b'IDAT' + compressed_data
    idat_crc = zlib.crc32(b'IDAT' + compressed_data) & 0xffffffff
    idat_chunk += struct.pack('>I', idat_crc)

    # IEND chunk
    iend_chunk = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', 0xae426082)

    return png_signature + ihdr_chunk + idat_chunk + iend_chunk

def main():
    """Create test sprites."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Create character sprite (simple colored grid)
    print("Creating test character sprite...")
    char_data = create_test_sprite_sheet()
    char_path = os.path.join(project_root, 'assets', 'characters', 'player', 'player_character_wizard.png')
    with open(char_path, 'wb') as f:
        f.write(char_data)
    print(f"Created: {char_path}")

    # Copy for NPCs
    npc_path = os.path.join(project_root, 'assets', 'characters', 'npcs', 'npc_sprites.png')
    with open(npc_path, 'wb') as f:
        f.write(char_data)
    print(f"Created: {npc_path}")

    # Create tile sprites (different colors)
    print("Creating test tile sprites...")
    tile_data = create_test_sprite_sheet()
    interior_path = os.path.join(project_root, 'assets', 'tilesets', 'interior', 'interior_tileset.png')
    with open(interior_path, 'wb') as f:
        f.write(tile_data)
    print(f"Created: {interior_path}")

    exterior_path = os.path.join(project_root, 'assets', 'tilesets', 'exterior', 'exterior_tileset.png')
    with open(exterior_path, 'wb') as f:
        f.write(tile_data)
    print(f"Created: {exterior_path}")

    # Create chess assets
    chess_data = create_test_sprite_sheet()
    chess_path = os.path.join(project_root, 'assets', 'chess', 'board', 'chess_board.png')
    with open(chess_path, 'wb') as f:
        f.write(chess_data)
    print(f"Created: {chess_path}")

    pieces_data = create_test_sprite_sheet()
    pieces_path = os.path.join(project_root, 'assets', 'chess', 'pieces', 'chess_pieces.png')
    with open(pieces_path, 'wb') as f:
        f.write(pieces_data)
    print(f"Created: {pieces_path}")

    # Create UI kit (simple colored areas)
    ui_data = create_simple_png(512, 256, 100, 150, 200, 255)  # Light blue
    ui_path = os.path.join(project_root, 'assets', 'ui', 'ui_kit.png')
    with open(ui_path, 'wb') as f:
        f.write(ui_data)
    print(f"Created: {ui_path}")

    print("\nTest sprites created! Now regenerate the resource files.")

if __name__ == '__main__':
    main()