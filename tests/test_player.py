# tests/test_player.py
import pytest
from unittest.mock import MagicMock
from player import Player
from settings import TILE_SIZE, PLAYER_LIVES, TILE_DOT, TILE_POWER, SCORE_DOT


def make_maze(walls=None):
    maze = MagicMock()
    walls = walls or set()
    maze.is_wall.side_effect = lambda col, row: (col, row) in walls
    maze.collect.return_value = 0
    return maze


def test_player_initial_position():
    maze = make_maze()
    player = Player(start_col=12, start_row=14, maze=maze)
    assert player.col == 12
    assert player.row == 14


def test_player_moves_right():
    maze = make_maze()
    player = Player(start_col=5, start_row=5, maze=maze)
    player.set_direction(1, 0)
    player.snap_to_grid()
    player.update(1.0)
    assert player.col > 5


def test_player_blocked_by_wall():
    maze = make_maze(walls={(6, 5)})
    player = Player(start_col=5, start_row=5, maze=maze)
    player.set_direction(1, 0)
    player.snap_to_grid()
    player.update(10.0)
    assert player.col <= 5


def test_player_collects_dot():
    maze = make_maze()
    maze.collect.return_value = TILE_DOT
    player = Player(start_col=5, start_row=5, maze=maze)
    player.set_direction(1, 0)
    player.snap_to_grid()
    player.update(0.5)
    assert maze.collect.called


def test_player_power_mode():
    maze = make_maze()
    maze.collect.return_value = TILE_POWER
    player = Player(start_col=5, start_row=5, maze=maze)
    player.set_direction(1, 0)
    player.snap_to_grid()
    player.update(0.5)
    assert player.powered_up


def test_player_power_expires():
    maze = make_maze()
    player = Player(start_col=5, start_row=5, maze=maze)
    player.activate_power(duration=0.1)
    player.update(0.2)
    assert not player.powered_up


def test_player_loses_life():
    maze = make_maze()
    player = Player(start_col=5, start_row=5, maze=maze)
    assert player.lives == PLAYER_LIVES
    player.die()
    assert player.lives == PLAYER_LIVES - 1


def test_player_game_over():
    maze = make_maze()
    player = Player(start_col=5, start_row=5, maze=maze)
    player.die()
    player.die()
    player.die()
    assert player.lives == 0
    assert player.is_dead()
