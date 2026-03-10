# sprite_loader.py
import os
import pygame
from settings import TILE_SIZE


def load_image(path: str, size=(TILE_SIZE, TILE_SIZE)) -> pygame.Surface:
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, size)


def load_player_sprites(base_dir="assets/sprites/border_collie") -> dict:
    """
    Returns dict: {((dx, dy), frame): Surface}
    Expects files: right_0.png, right_1.png, right_2.png, left_0.png, etc.
    Returns empty dict if directory or files are missing (fallback to pygame.draw).
    """
    sprites = {}
    if not os.path.isdir(base_dir):
        return sprites
    directions = {(1, 0): "right", (-1, 0): "left", (0, -1): "up", (0, 1): "down"}
    for (dx, dy), name in directions.items():
        for frame in range(3):
            path = os.path.join(base_dir, f"{name}_{frame}.png")
            if os.path.exists(path):
                sprites[((dx, dy), frame)] = load_image(path)
    return sprites


def load_ghost_sprites(personality_name: str,
                       base_dir="assets/sprites/beagle") -> dict:
    """
    Returns dict with keys 'normal' and/or 'scared'.
    Returns empty dict if files are missing.
    """
    sprites = {}
    if not os.path.isdir(base_dir):
        return sprites
    normal_path = os.path.join(base_dir, f"{personality_name}_normal.png")
    scared_path = os.path.join(base_dir, "scared.png")
    if os.path.exists(normal_path):
        sprites["normal"] = load_image(normal_path)
    if os.path.exists(scared_path):
        sprites["scared"] = load_image(scared_path)
    return sprites
