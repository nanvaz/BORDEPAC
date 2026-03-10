# tests/test_maze.py
import pytest
from maze import Maze
from settings import TILE_WALL, TILE_DOT, TILE_POWER, TILE_EMPTY, COLS, ROWS

def test_maze_dimensions():
    maze = Maze()
    assert len(maze.grid) == ROWS
    assert len(maze.grid[0]) == COLS

def test_maze_has_dots():
    maze = Maze()
    dots = sum(row.count(TILE_DOT) for row in maze.grid)
    assert dots > 0

def test_maze_has_power_ups():
    maze = Maze()
    powers = sum(row.count(TILE_POWER) for row in maze.grid)
    assert powers == 4  # PAC-Man clássico tem 4 power-ups

def test_maze_is_wall():
    maze = Maze()
    # Bordas devem ser parede
    assert maze.is_wall(0, 0)

def test_maze_is_not_wall():
    maze = Maze()
    # Interior com caminho não é parede
    # Encontrar primeira célula vazia
    for row in range(ROWS):
        for col in range(COLS):
            if maze.grid[row][col] != TILE_WALL:
                assert not maze.is_wall(col, row)
                return

def test_collect_dot():
    maze = Maze()
    # Encontrar uma bolinha
    for row in range(ROWS):
        for col in range(COLS):
            if maze.grid[row][col] == TILE_DOT:
                result = maze.collect(col, row)
                assert result == TILE_DOT
                assert maze.grid[row][col] == TILE_EMPTY
                return

def test_collect_power():
    maze = Maze()
    for row in range(ROWS):
        for col in range(COLS):
            if maze.grid[row][col] == TILE_POWER:
                result = maze.collect(col, row)
                assert result == TILE_POWER
                assert maze.grid[row][col] == TILE_EMPTY
                return

def test_all_collected():
    maze = Maze()
    # Coletar tudo manualmente
    for row in range(ROWS):
        for col in range(COLS):
            if maze.grid[row][col] in (TILE_DOT, TILE_POWER):
                maze.collect(col, row)
    assert maze.all_collected()

def test_not_all_collected():
    maze = Maze()
    assert not maze.all_collected()

def test_reset_restores_dots():
    maze = Maze()
    original_dots = sum(row.count(TILE_DOT) for row in maze.grid)
    for row in range(ROWS):
        for col in range(COLS):
            maze.collect(col, row)
    maze.reset()
    assert sum(row.count(TILE_DOT) for row in maze.grid) == original_dots
