# maze.py
import copy
from settings import (
    TILE_EMPTY, TILE_WALL, TILE_DOT, TILE_POWER,
    COLS, ROWS, TILE_SIZE,
    DARK_BLUE, WALL_COLOR, DOT_COLOR, POWER_COLOR
)

# Labirinto 25x18 — baseado no layout clássico PAC-Man
# 0=vazio, 1=parede, 2=bolinha, 3=power-up
_LAYOUT = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,3,1,1,2,1,1,1,2,1,1,2,1,2,1,1,2,1,1,1,2,1,1,3,1],
    [1,2,1,1,2,1,1,1,2,1,1,2,1,2,1,1,2,1,1,1,2,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,2,1,2,1,1,1,1,1,1,1,1,1,1,1,2,1,2,1,1,2,1],
    [1,2,2,2,2,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1,2,2,2,2,1],
    [1,1,1,1,2,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,2,1,1,1,1],
    [0,0,0,1,2,1,1,1,0,1,1,0,0,0,1,1,0,1,1,1,2,1,0,0,0],
    [0,0,0,1,2,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,2,1,0,0,0],
    [0,0,0,1,2,1,1,1,0,1,1,1,1,1,1,1,0,1,1,1,2,1,0,0,0],
    [1,1,1,1,2,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,2,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,2,1,1,1,2,1,1,2,1,2,1,1,2,1,1,1,2,1,1,2,1],
    [1,3,2,1,2,2,2,2,2,2,2,2,0,2,2,2,2,2,2,2,2,1,2,3,1],
    [1,1,2,1,2,1,2,1,1,1,1,1,1,1,1,1,1,1,2,1,2,1,2,1,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]


class Maze:
    def __init__(self):
        self._original = [row[:] for row in _LAYOUT]
        self.grid = [row[:] for row in _LAYOUT]

    def is_wall(self, col: int, row: int) -> bool:
        if row < 0 or row >= ROWS or col < 0 or col >= COLS:
            return True
        return self.grid[row][col] == TILE_WALL

    def collect(self, col: int, row: int) -> int:
        """Remove bolinha/power-up da célula. Retorna o tipo coletado (ou TILE_EMPTY)."""
        tile = self.grid[row][col]
        if tile in (TILE_DOT, TILE_POWER):
            self.grid[row][col] = TILE_EMPTY
        return tile

    def all_collected(self) -> bool:
        for row in self.grid:
            if TILE_DOT in row or TILE_POWER in row:
                return False
        return True

    def reset(self):
        self.grid = [row[:] for row in self._original]

    def draw(self, surface):
        import pygame
        for row_idx, row in enumerate(self.grid):
            for col_idx, tile in enumerate(row):
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                if tile == TILE_WALL:
                    pygame.draw.rect(surface, WALL_COLOR, rect)
                elif tile == TILE_DOT:
                    pygame.draw.circle(surface, DOT_COLOR,
                                       (x + TILE_SIZE // 2, y + TILE_SIZE // 2), 4)
                elif tile == TILE_POWER:
                    pygame.draw.circle(surface, POWER_COLOR,
                                       (x + TILE_SIZE // 2, y + TILE_SIZE // 2), 9)
