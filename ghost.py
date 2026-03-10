# ghost.py
import pygame
import random
import math
from enum import Enum
from settings import (
    TILE_SIZE, GHOST_BASE_SPEED, COLS, ROWS,
    GHOST_SCARED_COLOR, GHOST_FLASH_COLOR, WHITE,
)

FLASH_THRESHOLD = 2.0
DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]


class GhostPersonality(Enum):
    BISCUIT = "biscuit"
    CARAMEL = "caramel"
    PEPPER  = "pepper"
    NUGGET  = "nugget"


class Ghost:
    COLORS = {
        GhostPersonality.BISCUIT: (255, 0, 0),
        GhostPersonality.CARAMEL: (255, 180, 200),
        GhostPersonality.PEPPER:  (0, 220, 220),
        GhostPersonality.NUGGET:  (255, 160, 30),
    }

    def __init__(self, start_col: int, start_row: int,
                 personality: GhostPersonality, maze):
        self.start_col = start_col
        self.start_row = start_row
        self.personality = personality
        self.maze = maze

        self.col = start_col
        self.row = start_row
        self.x = float(start_col * TILE_SIZE)
        self.y = float(start_row * TILE_SIZE)

        self.dx = 0
        self.dy = -1
        self.speed = GHOST_BASE_SPEED
        self.scared = False
        self._scared_timer = 0.0

        self._sprites = {}
        self._color = self.COLORS[personality]
        self._anim_timer = 0.0
        self._flash_on = True

    def set_scared(self, duration: float):
        self.scared = True
        self._scared_timer = duration

    def is_flashing(self) -> bool:
        return self.scared and self._scared_timer <= FLASH_THRESHOLD

    def _get_target(self, player):
        if self.scared:
            return (self.col + (self.col - player.col),
                    self.row + (self.row - player.row))
        if self.personality == GhostPersonality.BISCUIT:
            return player.col, player.row
        elif self.personality == GhostPersonality.CARAMEL:
            return player.col + player.dx * 4, player.row + player.dy * 4
        elif self.personality == GhostPersonality.PEPPER:
            if random.random() < 0.5:
                return player.col, player.row
            return random.randint(0, COLS - 1), random.randint(0, ROWS - 1)
        elif self.personality == GhostPersonality.NUGGET:
            dist = math.hypot(self.col - player.col, self.row - player.row)
            if dist < 8:
                return COLS - 1 - player.col, ROWS - 1 - player.row
            return player.col, player.row
        return player.col, player.row

    def _choose_direction(self, player):
        target_col, target_row = self._get_target(player)
        best_dir = None
        best_dist = float('inf')
        dirs = list(DIRECTIONS)
        random.shuffle(dirs)
        reverse = (-self.dx, -self.dy)
        passable = [d for d in dirs if not self.maze.is_wall(self.col + d[0], self.row + d[1])]
        for d in dirs:
            if d == reverse and len(passable) > 1:
                continue
            nc, nr = self.col + d[0], self.row + d[1]
            if self.maze.is_wall(nc, nr):
                continue
            dist = math.hypot(nc - target_col, nr - target_row)
            if dist < best_dist:
                best_dist = dist
                best_dir = d
        return best_dir or (0, 0)

    def update(self, dt: float, player):
        if self.scared:
            self._scared_timer -= dt
            if self._scared_timer <= 0:
                self.scared = False
                self._scared_timer = 0.0

        cx = int(self.x / TILE_SIZE + 0.5) * TILE_SIZE
        cy = int(self.y / TILE_SIZE + 0.5) * TILE_SIZE
        aligned = (abs(self.x - cx) < 2 and abs(self.y - cy) < 2)

        if aligned:
            self.x = float(cx)
            self.y = float(cy)
            self.col = cx // TILE_SIZE
            self.row = cy // TILE_SIZE
            new_dir = self._choose_direction(player)
            self.dx, self.dy = new_dir

        move_pixels = self.speed * TILE_SIZE * dt
        self.x += self.dx * move_pixels
        self.y += self.dy * move_pixels

        self._anim_timer += dt
        if self._anim_timer >= 0.25:
            self._anim_timer = 0.0
            self._flash_on = not self._flash_on

    def reset(self):
        self.col = self.start_col
        self.row = self.start_row
        self.x = float(self.start_col * TILE_SIZE)
        self.y = float(self.start_row * TILE_SIZE)
        self.scared = False
        self._scared_timer = 0.0
        self.dx = 0
        self.dy = -1

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x) + 4, int(self.y) + 4, TILE_SIZE - 8, TILE_SIZE - 8)

    def draw(self, surface: pygame.Surface):
        if self.scared:
            color = GHOST_FLASH_COLOR if (self.is_flashing() and not self._flash_on) else GHOST_SCARED_COLOR
        else:
            color = self._color

        cx = int(self.x) + TILE_SIZE // 2
        cy = int(self.y) + TILE_SIZE // 2
        r = TILE_SIZE // 2 - 2

        pygame.draw.circle(surface, color, (cx, cy - r // 4), r)
        pygame.draw.rect(surface, color,
                         pygame.Rect(int(self.x) + 2, cy - r // 4, TILE_SIZE - 4, r))
        if not self.scared:
            pygame.draw.circle(surface, WHITE, (cx - 4, cy - r // 4 - 2), 3)
            pygame.draw.circle(surface, WHITE, (cx + 4, cy - r // 4 - 2), 3)
            pygame.draw.circle(surface, (0, 0, 200), (cx - 4 + self.dx, cy - r // 4 - 2 + self.dy), 2)
            pygame.draw.circle(surface, (0, 0, 200), (cx + 4 + self.dx, cy - r // 4 - 2 + self.dy), 2)

    def load_sprites(self, sprites: dict):
        self._sprites = sprites
