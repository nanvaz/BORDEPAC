# tests/test_ghost.py
import pytest
from unittest.mock import MagicMock
from ghost import Ghost, GhostPersonality
from settings import TILE_SIZE


def make_maze(walls=None):
    maze = MagicMock()
    walls = walls or set()
    maze.is_wall.side_effect = lambda col, row: (col, row) in walls
    return maze


def make_player(col=12, row=14, dx=1, dy=0):
    p = MagicMock()
    p.col = col
    p.row = row
    p.dx = dx
    p.dy = dy
    p.powered_up = False
    return p


def test_ghost_initial_position():
    maze = make_maze()
    ghost = Ghost(start_col=11, start_row=9, personality=GhostPersonality.BISCUIT, maze=maze)
    assert ghost.col == 11
    assert ghost.row == 9


def test_ghost_not_scared_initially():
    maze = make_maze()
    ghost = Ghost(start_col=11, start_row=9, personality=GhostPersonality.BISCUIT, maze=maze)
    assert not ghost.scared


def test_ghost_becomes_scared():
    maze = make_maze()
    ghost = Ghost(start_col=11, start_row=9, personality=GhostPersonality.BISCUIT, maze=maze)
    ghost.set_scared(duration=10.0)
    assert ghost.scared


def test_ghost_scared_expires():
    maze = make_maze()
    ghost = Ghost(start_col=11, start_row=9, personality=GhostPersonality.BISCUIT, maze=maze)
    ghost.set_scared(duration=0.1)
    ghost.update(dt=0.2, player=make_player())
    assert not ghost.scared


def test_ghost_reset_returns_home():
    maze = make_maze()
    ghost = Ghost(start_col=11, start_row=9, personality=GhostPersonality.BISCUIT, maze=maze)
    ghost.col = 5
    ghost.row = 5
    ghost.reset()
    assert ghost.col == 11
    assert ghost.row == 9


def test_ghost_get_rect():
    import pygame
    maze = make_maze()
    ghost = Ghost(start_col=5, start_row=5, personality=GhostPersonality.BISCUIT, maze=maze)
    rect = ghost.get_rect()
    assert isinstance(rect, pygame.Rect)


def test_ghost_flashing_near_end():
    maze = make_maze()
    ghost = Ghost(start_col=11, start_row=9, personality=GhostPersonality.NUGGET, maze=maze)
    ghost.set_scared(duration=2.0)
    ghost.update(dt=1.5, player=make_player())
    assert ghost.is_flashing()


def test_ghost_not_flashing_when_calm():
    maze = make_maze()
    ghost = Ghost(start_col=11, start_row=9, personality=GhostPersonality.NUGGET, maze=maze)
    assert not ghost.is_flashing()
