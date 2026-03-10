# player.py
import pygame
from settings import (
    TILE_SIZE, PLAYER_SPEED, PLAYER_LIVES,
    TILE_DOT, TILE_POWER, TILE_EMPTY,
    SCORE_DOT, SCORE_POWER,
)


class Player:
    def __init__(self, start_col: int, start_row: int, maze):
        self.start_col = start_col
        self.start_row = start_row
        self.maze = maze

        self.col = start_col
        self.row = start_row
        self.x = float(start_col * TILE_SIZE)
        self.y = float(start_row * TILE_SIZE)

        self.dx = 0
        self.dy = 0
        self._next_dx = 0
        self._next_dy = 0

        self.speed = PLAYER_SPEED
        self.lives = PLAYER_LIVES
        self.score = 0

        self.powered_up = False
        self._power_timer = 0.0

        self._anim_timer = 0.0
        self._anim_frame = 0
        self._sprites = {}
        self._fallback_color = (255, 220, 0)

    def set_direction(self, dx: int, dy: int):
        self._next_dx = dx
        self._next_dy = dy

    def snap_to_grid(self):
        self.x = float(self.col * TILE_SIZE)
        self.y = float(self.row * TILE_SIZE)

    def activate_power(self, duration: float):
        self.powered_up = True
        self._power_timer = duration

    def update(self, dt: float):
        next_col = self.col + self._next_dx
        next_row = self.row + self._next_dy
        if not self.maze.is_wall(next_col, next_row):
            self.dx = self._next_dx
            self.dy = self._next_dy

        move_pixels = self.speed * TILE_SIZE * dt
        self.x += self.dx * move_pixels
        self.y += self.dy * move_pixels

        new_col = int(self.x / TILE_SIZE + 0.5)
        new_row = int(self.y / TILE_SIZE + 0.5)

        if new_col != self.col or new_row != self.row:
            if not self.maze.is_wall(new_col, new_row):
                self.col = new_col
                self.row = new_row
                tile = self.maze.collect(self.col, self.row)
                if tile == TILE_DOT:
                    self.score += SCORE_DOT
                elif tile == TILE_POWER:
                    self.score += SCORE_POWER
                    self.activate_power(10.0)  # default; game.py overrides via activate_power
            else:
                self.x = float(self.col * TILE_SIZE)
                self.y = float(self.row * TILE_SIZE)
                self.dx = 0
                self.dy = 0

        if self.powered_up:
            self._power_timer -= dt
            if self._power_timer <= 0:
                self.powered_up = False
                self._power_timer = 0.0

        self._anim_timer += dt
        if self._anim_timer >= 0.1:
            self._anim_timer = 0.0
            self._anim_frame = (self._anim_frame + 1) % 3

    def die(self):
        self.lives -= 1
        self.col = self.start_col
        self.row = self.start_row
        self.snap_to_grid()
        self.dx = 0
        self.dy = 0
        self.powered_up = False
        self._power_timer = 0.0

    def is_dead(self) -> bool:
        return self.lives <= 0

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x) + 4, int(self.y) + 4, TILE_SIZE - 8, TILE_SIZE - 8)

    def draw(self, surface: pygame.Surface):
        import math
        direction_key = (self.dx, self.dy)
        sprite_key = (direction_key, self._anim_frame)

        if sprite_key in self._sprites:
            surface.blit(self._sprites[sprite_key], (int(self.x), int(self.y)))
        else:
            cx = int(self.x) + TILE_SIZE // 2
            cy = int(self.y) + TILE_SIZE // 2
            r = TILE_SIZE // 2 - 2
            pygame.draw.circle(surface, self._fallback_color, (cx, cy), r)
            if self._anim_frame < 2:
                angle_map = {(1, 0): 0, (-1, 0): 180, (0, -1): 270, (0, 1): 90}
                angle = angle_map.get((self.dx, self.dy), 0)
                mouth_open = 30 * (3 - self._anim_frame)
                start_a = math.radians(angle + mouth_open)
                end_a = math.radians(angle - mouth_open)
                points = [(cx, cy)]
                for i in range(20):
                    a = start_a + (end_a - start_a) * i / 19
                    points.append((cx + r * math.cos(a), cy - r * math.sin(a)))
                pygame.draw.polygon(surface, (0, 0, 0), points)

    def load_sprites(self, sprites: dict):
        self._sprites = sprites
