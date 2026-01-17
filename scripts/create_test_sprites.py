#!/usr/bin/env python3
"""
Create simple test sprites for the Wizard Chess validation scenes.
Generates colored rectangles to test the animation and UI systems.
"""

from PIL import Image, ImageDraw
import os

def create_colored_rectangle(width, height, color):
    """Create a simple colored rectangle."""
    img = Image.new('RGBA', (width, height), color)
    return img

def create_character_sprite_sheet():
    """Create a simple character sprite sheet with colored rectangles."""
    frame_size = 64
    cols = 4  # 4 frames per animation
    rows = 4  # 4 animations: idle, walk_down, walk_up, walk_right

    sheet_width = cols * frame_size
    sheet_height = rows * frame_size

    # Create new image
    sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))

    # Colors for different animations
    colors = [
        (255, 100, 100, 255),  # Red - idle
        (100, 255, 100, 255),  # Green - walk_down
        (100, 100, 255, 255),  # Blue - walk_up
        (255, 255, 100, 255),  # Yellow - walk_right
    ]

    # Create frames
    for row in range(rows):
        for col in range(cols):
            x = col * frame_size
            y = row * frame_size

            # Create a colored rectangle with a border
            frame = create_colored_rectangle(frame_size, frame_size, colors[row])

            # Add a simple border
            draw = ImageDraw.Draw(frame)
            border_color = (255, 255, 255, 255)  # White border
            draw.rectangle([2, 2, frame_size-3, frame_size-3], outline=border_color, width=2)

            # Paste onto sheet
            sheet.paste(frame, (x, y))

    return sheet

def create_tile_sprite_sheet():
    """Create a simple tile sprite sheet."""
    tile_size = 32
    cols = 8
    rows = 6

    sheet_width = cols * tile_size
    sheet_height = rows * tile_size

    sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))

    # Different tile colors
    tile_colors = [
        (139, 69, 19, 255),   # Brown - floor
        (128, 128, 128, 255), # Gray - wall
        (0, 128, 0, 255),     # Green - grass
        (0, 0, 128, 255),     # Blue - water
        (128, 0, 128, 255),   # Purple - special
        (255, 165, 0, 255),   # Orange - accent
    ]

    for row in range(rows):
        for col in range(cols):
            x = col * tile_size
            y = row * tile_size

            color_index = (row * cols + col) % len(tile_colors)
            color = tile_colors[color_index]

            tile = create_colored_rectangle(tile_size, tile_size, color)

            # Add a simple border
            draw = ImageDraw.Draw(tile)
            border_color = (255, 255, 255, 255)
            draw.rectangle([1, 1, tile_size-2, tile_size-2], outline=border_color, width=1)

            sheet.paste(tile, (x, y))

    return sheet

def create_ui_sprite_sheet():
    """Create a simple UI sprite sheet."""
    # Create a smaller UI kit
    ui_width = 512
    ui_height = 256

    ui_sheet = Image.new('RGBA', (ui_width, ui_height), (0, 0, 0, 0))

    # Dialogue panel (top left)
    dialogue_panel = create_colored_rectangle(256, 64, (50, 50, 80, 255))
    draw = ImageDraw.Draw(dialogue_panel)
    draw.rectangle([5, 5, 251, 59], outline=(255, 255, 255, 255), width=2)
    ui_sheet.paste(dialogue_panel, (0, 0))

    # Menu panel (top right)
    menu_panel = create_colored_rectangle(200, 100, (80, 80, 50, 255))
    draw = ImageDraw.Draw(menu_panel)
    draw.rectangle([5, 5, 195, 95], outline=(255, 255, 255, 255), width=2)
    ui_sheet.paste(menu_panel, (256, 0))

    # Info panel (bottom left)
    info_panel = create_colored_rectangle(200, 80, (60, 80, 60, 255))
    draw = ImageDraw.Draw(info_panel)
    draw.rectangle([5, 5, 195, 75], outline=(255, 255, 255, 255), width=2)
    ui_sheet.paste(info_panel, (0, 100))

    # Buttons (bottom right area)
    button_normal = create_colored_rectangle(80, 24, (100, 100, 100, 255))
    draw = ImageDraw.Draw(button_normal)
    draw.rectangle([2, 2, 77, 21], outline=(255, 255, 255, 255), width=1)
    ui_sheet.paste(button_normal, (256, 120))

    button_hover = create_colored_rectangle(80, 24, (120, 120, 120, 255))
    draw = ImageDraw.Draw(button_hover)
    draw.rectangle([2, 2, 77, 21], outline=(255, 255, 255, 255), width=1)
    ui_sheet.paste(button_hover, (256, 150))

    button_pressed = create_colored_rectangle(80, 24, (80, 80, 80, 255))
    draw = ImageDraw.Draw(button_pressed)
    draw.rectangle([2, 2, 77, 21], outline=(255, 255, 255, 255), width=1)
    ui_sheet.paste(button_pressed, (256, 180))

    # Icons
    icon_chess = create_colored_rectangle(32, 32, (200, 200, 100, 255))
    draw = ImageDraw.Draw(icon_chess)
    draw.rectangle([2, 2, 29, 29], outline=(255, 255, 255, 255), width=1)
    ui_sheet.paste(icon_chess, (350, 120))

    icon_inventory = create_colored_rectangle(32, 32, (100, 200, 200, 255))
    draw = ImageDraw.Draw(icon_inventory)
    draw.rectangle([2, 2, 29, 29], outline=(255, 255, 255, 255), width=1)
    ui_sheet.paste(icon_inventory, (390, 120))

    icon_settings = create_colored_rectangle(32, 32, (200, 100, 200, 255))
    draw = ImageDraw.Draw(icon_settings)
    draw.rectangle([2, 2, 29, 29], outline=(255, 255, 255, 255), width=1)
    ui_sheet.paste(icon_settings, (430, 120))

    return ui_sheet

def main():
    """Create test sprites for all asset types."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Create character sprites
    print("Creating character sprites...")
    char_sheet = create_character_sprite_sheet()
    char_path = os.path.join(project_root, 'assets', 'characters', 'player', 'player_character_wizard.png')
    char_sheet.save(char_path)
    print(f"Saved: {char_path}")

    # Copy for NPCs
    npc_path = os.path.join(project_root, 'assets', 'characters', 'npcs', 'npc_sprites.png')
    char_sheet.save(npc_path)
    print(f"Saved: {npc_path}")

    # Create tile sprites
    print("Creating tile sprites...")
    tile_sheet = create_tile_sprite_sheet()
    interior_path = os.path.join(project_root, 'assets', 'tilesets', 'interior', 'interior_tileset.png')
    tile_sheet.save(interior_path)
    print(f"Saved: {interior_path}")

    exterior_path = os.path.join(project_root, 'assets', 'tilesets', 'exterior', 'exterior_tileset.png')
    tile_sheet.save(exterior_path)
    print(f"Saved: {exterior_path}")

    # Create chess board
    print("Creating chess board...")
    chess_sheet = create_tile_sprite_sheet()
    chess_path = os.path.join(project_root, 'assets', 'chess', 'board', 'chess_board.png')
    chess_sheet.save(chess_path)
    print(f"Saved: {chess_path}")

    # Create chess pieces (smaller sprites)
    print("Creating chess pieces...")
    piece_size = 32
    piece_sheet = Image.new('RGBA', (piece_size * 6, piece_size * 2), (0, 0, 0, 0))

    piece_colors = [
        (255, 255, 255, 255),  # White pieces
        (0, 0, 0, 255),        # Black pieces
    ]

    piece_types = ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king']

    for color_idx, color in enumerate(piece_colors):
        y = color_idx * piece_size
        for piece_idx, piece_type in enumerate(piece_types):
            x = piece_idx * piece_size

            piece = create_colored_rectangle(piece_size, piece_size, color)
            draw = ImageDraw.Draw(piece)
            draw.rectangle([2, 2, piece_size-3, piece_size-3], outline=(255, 255, 255, 255), width=1)

            piece_sheet.paste(piece, (x, y))

    pieces_path = os.path.join(project_root, 'assets', 'chess', 'pieces', 'chess_pieces.png')
    piece_sheet.save(pieces_path)
    print(f"Saved: {pieces_path}")

    # Create UI sprites
    print("Creating UI sprites...")
    ui_sheet = create_ui_sprite_sheet()
    ui_path = os.path.join(project_root, 'assets', 'ui', 'ui_kit.png')
    ui_sheet.save(ui_path)
    print(f"Saved: {ui_path}")

    print("\nTest sprites created! Now regenerate the resource files...")

if __name__ == '__main__':
    try:
        import PIL
        main()
    except ImportError:
        print("PIL/Pillow not installed. Install with: pip install Pillow")
        print("Creating placeholder sprites with basic colors...")

        # Fallback: create simple colored images
        create_fallback_sprites()