# BORDEPAC Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar um jogo PAC-Man com Border Collie comendo bolinhas de tênis, fugindo de Beagles, usando Python + Pygame.

**Architecture:** Game loop a 60 FPS em `game.py`, labirinto representado como matriz 2D em `maze.py`, lógica de entidades separada da renderização para facilitar testes. Sprites PNG do OpenGameArt com fallback para `pygame.draw`.

**Tech Stack:** Python 3.10+, Pygame 2.x, pytest

---

## Chunk 1: Setup do Projeto e Configurações

### Task 1: Estrutura de diretórios e dependências

**Files:**
- Create: `requirements.txt`
- Create: `requirements-dev.txt`
- Create: `settings.py`

- [ ] **Step 1: Criar requirements.txt**

```
pygame>=2.0.0
```

- [ ] **Step 2: Criar requirements-dev.txt**

```
pytest>=7.0.0
pytest-mock>=3.0.0
```

- [ ] **Step 3: Criar diretórios de assets**

```bash
mkdir -p assets/sprites assets/sounds assets/fonts
mkdir -p tests
touch tests/__init__.py
```

- [ ] **Step 4: Criar settings.py**

```python
# settings.py
# Tela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "BORDEPAC"

# Grid
TILE_SIZE = 32
COLS = 25
ROWS = 18

# Cores
BLACK = (0, 0, 0)
DARK_BLUE = (0, 0, 40)
WALL_COLOR = (33, 93, 228)
DOT_COLOR = (200, 220, 80)      # amarelo-esverdeado (bolinha de tênis)
POWER_COLOR = (255, 230, 50)    # amarelo brilhante (power-up)
WHITE = (255, 255, 255)
GHOST_SCARED_COLOR = (30, 30, 180)
GHOST_FLASH_COLOR = (255, 255, 255)
HUD_COLOR = (255, 255, 255)

# Pontuação
SCORE_DOT = 10
SCORE_POWER = 50
SCORE_GHOST_BASE = 200          # dobra a cada Beagle consecutivo no mesmo power

# Velocidades (células por segundo)
PLAYER_SPEED = 5.0
GHOST_BASE_SPEED = 3.5
GHOST_SPEED_INCREMENT = 0.35    # +10% por fase

# Power-up
POWER_DURATION_BASE = 10.0      # segundos na fase 1
POWER_DURATION_MIN = 3.0
POWER_DURATION_DECREMENT = 1.0  # -1s por fase

# Vidas
PLAYER_LIVES = 3

# Tile types
TILE_EMPTY = 0
TILE_WALL = 1
TILE_DOT = 2
TILE_POWER = 3
```

- [ ] **Step 5: Instalar dependências**

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

- [ ] **Step 6: Commit**

```bash
git add requirements.txt requirements-dev.txt settings.py assets/ tests/
git commit -m "chore: project setup, settings and directory structure"
```

---

### Task 2: Labirinto — estrutura de dados e lógica

**Files:**
- Create: `maze.py`
- Create: `tests/test_maze.py`

- [ ] **Step 1: Escrever testes para o labirinto**

```python
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
```

- [ ] **Step 2: Rodar testes para confirmar que falham**

```bash
pytest tests/test_maze.py -v
```
Esperado: `ModuleNotFoundError: No module named 'maze'`

- [ ] **Step 3: Implementar maze.py**

```python
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
```

- [ ] **Step 4: Rodar testes**

```bash
pytest tests/test_maze.py -v
```
Esperado: todos passando.

- [ ] **Step 5: Commit**

```bash
git add maze.py tests/test_maze.py
git commit -m "feat: maze data structure with collect and reset logic"
```

---

## Chunk 2: Player (Border Collie)

### Task 3: Lógica de movimento do player

**Files:**
- Create: `player.py`
- Create: `tests/test_player.py`

- [ ] **Step 1: Escrever testes de movimento**

```python
# tests/test_player.py
import pytest
from unittest.mock import MagicMock
from player import Player
from settings import TILE_SIZE, COLS, ROWS

def make_maze(walls=None):
    """Cria um mock de maze sem paredes (exceto onde especificado)."""
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
    player.update(1.0)  # 1 segundo
    assert player.col > 5

def test_player_blocked_by_wall():
    maze = make_maze(walls={(6, 5)})
    player = Player(start_col=5, start_row=5, maze=maze)
    player.set_direction(1, 0)
    player.snap_to_grid()
    player.update(10.0)  # tempo suficiente para chegar à parede
    # Não deve ultrapassar a parede
    assert player.col <= 5

def test_player_collects_dot():
    from settings import TILE_DOT, SCORE_DOT
    maze = make_maze()
    maze.collect.return_value = TILE_DOT
    player = Player(start_col=5, start_row=5, maze=maze)
    player.set_direction(1, 0)
    player.snap_to_grid()
    player.update(0.5)
    # collect deve ter sido chamado
    assert maze.collect.called

def test_player_power_mode():
    from settings import TILE_POWER, POWER_DURATION_BASE
    maze = make_maze()
    maze.collect.return_value = TILE_POWER
    player = Player(start_col=5, start_row=5, maze=maze)
    player.set_direction(1, 0)
    player.snap_to_grid()
    player.update(0.5)
    assert player.powered_up

def test_player_power_expires():
    from settings import TILE_POWER
    maze = make_maze()
    maze.collect.return_value = TILE_POWER
    player = Player(start_col=5, start_row=5, maze=maze)
    player.activate_power(duration=0.1)
    player.update(0.2)
    assert not player.powered_up

def test_player_loses_life():
    maze = make_maze()
    from settings import PLAYER_LIVES
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
```

- [ ] **Step 2: Rodar testes para confirmar que falham**

```bash
pytest tests/test_player.py -v
```
Esperado: `ModuleNotFoundError: No module named 'player'`

- [ ] **Step 3: Implementar player.py**

```python
# player.py
import pygame
from settings import (
    TILE_SIZE, PLAYER_SPEED, PLAYER_LIVES,
    TILE_DOT, TILE_POWER, TILE_EMPTY,
    SCORE_DOT, SCORE_POWER, COLS, ROWS
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

        # Animação
        self._anim_timer = 0.0
        self._anim_frame = 0
        self._sprites = {}  # carregado por SpriteLoader
        self._fallback_color = (255, 220, 0)

    # --- Controle ---

    def set_direction(self, dx: int, dy: int):
        self._next_dx = dx
        self._next_dy = dy

    def snap_to_grid(self):
        self.x = float(self.col * TILE_SIZE)
        self.y = float(self.row * TILE_SIZE)

    # --- Power-up ---

    def activate_power(self, duration: float):
        self.powered_up = True
        self._power_timer = duration

    # --- Update ---

    def update(self, dt: float):
        # Tenta mudar direção se solicitado
        next_col = self.col + self._next_dx
        next_row = self.row + self._next_dy
        if not self.maze.is_wall(next_col, next_row):
            self.dx = self._next_dx
            self.dy = self._next_dy

        # Move
        move_pixels = self.speed * TILE_SIZE * dt
        self.x += self.dx * move_pixels
        self.y += self.dy * move_pixels

        # Detecta chegada em nova célula
        new_col = int(self.x / TILE_SIZE + 0.5)
        new_row = int(self.y / TILE_SIZE + 0.5)

        if new_col != self.col or new_row != self.row:
            if not self.maze.is_wall(new_col, new_row):
                self.col = new_col
                self.row = new_row
                # Coleta
                tile = self.maze.collect(self.col, self.row)
                if tile == TILE_DOT:
                    self.score += SCORE_DOT
                elif tile == TILE_POWER:
                    self.score += SCORE_POWER
                    # Duração é gerenciada pelo Game, que chama activate_power
            else:
                # Bate na parede — snap de volta
                self.x = float(self.col * TILE_SIZE)
                self.y = float(self.row * TILE_SIZE)
                self.dx = 0
                self.dy = 0

        # Power timer
        if self.powered_up:
            self._power_timer -= dt
            if self._power_timer <= 0:
                self.powered_up = False
                self._power_timer = 0.0

        # Animação
        self._anim_timer += dt
        if self._anim_timer >= 0.1:
            self._anim_timer = 0.0
            self._anim_frame = (self._anim_frame + 1) % 3

    # --- Vida ---

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

    # --- Colisão com fantasmas ---

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x) + 4, int(self.y) + 4, TILE_SIZE - 8, TILE_SIZE - 8)

    # --- Renderização ---

    def draw(self, surface: pygame.Surface):
        direction_key = (self.dx, self.dy)
        sprite_key = (direction_key, self._anim_frame)

        if sprite_key in self._sprites:
            surface.blit(self._sprites[sprite_key], (int(self.x), int(self.y)))
        else:
            # Fallback: círculo amarelo com "boca" (triângulo)
            cx = int(self.x) + TILE_SIZE // 2
            cy = int(self.y) + TILE_SIZE // 2
            r = TILE_SIZE // 2 - 2
            pygame.draw.circle(surface, self._fallback_color, (cx, cy), r)
            if self._anim_frame < 2:
                # Boca aberta
                import math
                angle_map = {
                    (1, 0): 0, (-1, 0): 180, (0, -1): 270, (0, 1): 90
                }
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
        """sprites: {((dx,dy), frame): pygame.Surface}"""
        self._sprites = sprites
```

- [ ] **Step 4: Rodar testes**

```bash
pytest tests/test_player.py -v
```
Esperado: todos passando.

- [ ] **Step 5: Commit**

```bash
git add player.py tests/test_player.py
git commit -m "feat: player movement, collection, power-up and life logic"
```

---

## Chunk 3: Ghosts (Beagles)

### Task 4: Classe Ghost e IA

**Files:**
- Create: `ghost.py`
- Create: `tests/test_ghost.py`

- [ ] **Step 1: Escrever testes para ghost**

```python
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
    ghost.update(dt=1.5, player=make_player())  # restam 0.5s
    assert ghost.is_flashing()

def test_ghost_not_flashing_when_calm():
    maze = make_maze()
    ghost = Ghost(start_col=11, start_row=9, personality=GhostPersonality.NUGGET, maze=maze)
    assert not ghost.is_flashing()
```

- [ ] **Step 2: Rodar testes para confirmar que falham**

```bash
pytest tests/test_ghost.py -v
```
Esperado: `ModuleNotFoundError: No module named 'ghost'`

- [ ] **Step 3: Implementar ghost.py**

```python
# ghost.py
import pygame
import random
import math
from enum import Enum
from settings import (
    TILE_SIZE, GHOST_BASE_SPEED, COLS, ROWS,
    GHOST_SCARED_COLOR, GHOST_FLASH_COLOR, WHITE
)

FLASH_THRESHOLD = 2.0  # segundos restantes para começar a piscar


class GhostPersonality(Enum):
    BISCUIT = "biscuit"   # persegue diretamente
    CARAMEL = "caramel"   # corta caminho
    PEPPER = "pepper"     # semi-aleatório
    NUGGET = "nugget"     # foge quando perto, aproxima quando longe


DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]


class Ghost:
    COLORS = {
        GhostPersonality.BISCUIT: (255, 0, 0),
        GhostPersonality.CARAMEL: (255, 180, 200),
        GhostPersonality.PEPPER: (0, 220, 220),
        GhostPersonality.NUGGET: (255, 160, 30),
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

    # --- Scared ---

    def set_scared(self, duration: float):
        self.scared = True
        self._scared_timer = duration

    def is_flashing(self) -> bool:
        return self.scared and self._scared_timer <= FLASH_THRESHOLD

    # --- AI ---

    def _choose_direction(self, player) -> tuple:
        """Escolhe próxima direção baseado na personalidade."""
        target_col, target_row = self._get_target(player)
        best_dir = None
        best_dist = float('inf')

        # Embaralha para quebrar empates de forma aleatória
        dirs = list(DIRECTIONS)
        random.shuffle(dirs)

        # Não pode inverter direção (exceto se encurralado)
        reverse = (-self.dx, -self.dy)

        for d in dirs:
            if d == reverse and len([dd for dd in dirs if not self.maze.is_wall(self.col + dd[0], self.row + dd[1])]) > 1:
                continue
            nc, nr = self.col + d[0], self.row + d[1]
            if self.maze.is_wall(nc, nr):
                continue
            dist = math.hypot(nc - target_col, nr - target_row)
            if dist < best_dist:
                best_dist = dist
                best_dir = d

        return best_dir or (0, 0)

    def _get_target(self, player) -> tuple:
        if self.scared:
            # Foge do player — target oposto
            return (
                self.col + (self.col - player.col),
                self.row + (self.row - player.row)
            )

        if self.personality == GhostPersonality.BISCUIT:
            return player.col, player.row

        elif self.personality == GhostPersonality.CARAMEL:
            # 4 tiles à frente do player
            return player.col + player.dx * 4, player.row + player.dy * 4

        elif self.personality == GhostPersonality.PEPPER:
            # 50% chance de perseguir, 50% aleatório
            if random.random() < 0.5:
                return player.col, player.row
            return random.randint(0, COLS - 1), random.randint(0, ROWS - 1)

        elif self.personality == GhostPersonality.NUGGET:
            dist = math.hypot(self.col - player.col, self.row - player.row)
            if dist < 8:
                # Foge para canto oposto
                return COLS - 1 - player.col, ROWS - 1 - player.row
            return player.col, player.row

        return player.col, player.row

    # --- Update ---

    def update(self, dt: float, player):
        if self.scared:
            self._scared_timer -= dt
            if self._scared_timer <= 0:
                self.scared = False
                self._scared_timer = 0.0

        # Decide nova direção quando alinhado ao grid
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

        # Flash timer
        self._anim_timer += dt
        if self._anim_timer >= 0.25:
            self._anim_timer = 0.0
            self._flash_on = not self._flash_on

    # --- Reset ---

    def reset(self):
        self.col = self.start_col
        self.row = self.start_row
        self.x = float(self.start_col * TILE_SIZE)
        self.y = float(self.start_row * TILE_SIZE)
        self.scared = False
        self._scared_timer = 0.0
        self.dx = 0
        self.dy = -1

    # --- Colisão ---

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x) + 4, int(self.y) + 4, TILE_SIZE - 8, TILE_SIZE - 8)

    # --- Renderização ---

    def draw(self, surface: pygame.Surface):
        if self.scared:
            color = GHOST_FLASH_COLOR if (self.is_flashing() and not self._flash_on) else GHOST_SCARED_COLOR
        else:
            color = self._color

        cx = int(self.x) + TILE_SIZE // 2
        cy = int(self.y) + TILE_SIZE // 2
        r = TILE_SIZE // 2 - 2

        # Corpo do fantasma (Beagle simplificado)
        pygame.draw.circle(surface, color, (cx, cy - r // 4), r)
        pygame.draw.rect(surface, color,
                         pygame.Rect(int(self.x) + 2, cy - r // 4, TILE_SIZE - 4, r))
        # Olhos brancos
        if not self.scared:
            pygame.draw.circle(surface, WHITE, (cx - 4, cy - r // 4 - 2), 3)
            pygame.draw.circle(surface, WHITE, (cx + 4, cy - r // 4 - 2), 3)
            pygame.draw.circle(surface, (0, 0, 200), (cx - 4 + self.dx, cy - r // 4 - 2 + self.dy), 2)
            pygame.draw.circle(surface, (0, 0, 200), (cx + 4 + self.dx, cy - r // 4 - 2 + self.dy), 2)

    def load_sprites(self, sprites: dict):
        self._sprites = sprites
```

- [ ] **Step 4: Rodar testes**

```bash
pytest tests/test_ghost.py -v
```
Esperado: todos passando.

- [ ] **Step 5: Commit**

```bash
git add ghost.py tests/test_ghost.py
git commit -m "feat: ghost AI with 4 personalities (Biscuit, Caramel, Pepper, Nugget)"
```

---

## Chunk 4: HUD, Game e Main

### Task 5: HUD

**Files:**
- Create: `hud.py`

- [ ] **Step 1: Implementar hud.py**

```python
# hud.py
import pygame
from settings import SCREEN_WIDTH, HUD_COLOR, TILE_SIZE, WHITE, DOT_COLOR

HUD_HEIGHT = 40
FONT_SIZE = 24


class HUD:
    def __init__(self, screen_width: int):
        self.screen_width = screen_width
        self._font = None  # inicializado em init()

    def init(self):
        self._font = pygame.font.SysFont("monospace", FONT_SIZE, bold=True)

    def draw(self, surface: pygame.Surface, score: int, lives: int, level: int):
        y = surface.get_height() - HUD_HEIGHT

        # Fundo do HUD
        pygame.draw.rect(surface, (0, 0, 20),
                         pygame.Rect(0, y, self.screen_width, HUD_HEIGHT))

        # Pontuação
        score_surf = self._font.render(f"SCORE: {score:05d}", True, HUD_COLOR)
        surface.blit(score_surf, (10, y + 8))

        # Fase
        level_surf = self._font.render(f"FASE {level}", True, HUD_COLOR)
        lw = level_surf.get_width()
        surface.blit(level_surf, (self.screen_width // 2 - lw // 2, y + 8))

        # Vidas (círculos representando Border Collies miniatura)
        for i in range(lives):
            cx = self.screen_width - 30 - i * 28
            cy = y + HUD_HEIGHT // 2
            pygame.draw.circle(surface, DOT_COLOR, (cx, cy), 10)

    def draw_message(self, surface: pygame.Surface, text: str, color=None):
        color = color or WHITE
        big_font = pygame.font.SysFont("monospace", 48, bold=True)
        surf = big_font.render(text, True, color)
        x = surface.get_width() // 2 - surf.get_width() // 2
        y = surface.get_height() // 2 - surf.get_height() // 2
        surface.blit(surf, (x, y))
```

- [ ] **Step 2: Commit**

```bash
git add hud.py
git commit -m "feat: HUD with score, level, and lives display"
```

---

### Task 6: Game — orquestração principal

**Files:**
- Create: `game.py`

- [ ] **Step 1: Implementar game.py**

```python
# game.py
import pygame
import sys
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TILE_SIZE, DARK_BLUE,
    GHOST_BASE_SPEED, GHOST_SPEED_INCREMENT,
    POWER_DURATION_BASE, POWER_DURATION_DECREMENT, POWER_DURATION_MIN,
    SCORE_GHOST_BASE, PLAYER_LIVES
)
from maze import Maze
from player import Player
from ghost import Ghost, GhostPersonality
from hud import HUD


GHOST_CONFIGS = [
    {"col": 11, "row": 9,  "personality": GhostPersonality.BISCUIT},
    {"col": 12, "row": 9,  "personality": GhostPersonality.CARAMEL},
    {"col": 13, "row": 9,  "personality": GhostPersonality.PEPPER},
    {"col": 12, "row": 10, "personality": GhostPersonality.NUGGET},
]

PLAYER_START = {"col": 12, "row": 14}


class GameState:
    PLAYING = "playing"
    DYING = "dying"
    LEVEL_COMPLETE = "level_complete"
    GAME_OVER = "game_over"


class Game:
    def __init__(self, surface: pygame.Surface):
        self.surface = surface
        self.clock = pygame.time.Clock()
        self.level = 1
        self.state = GameState.PLAYING
        self._state_timer = 0.0
        self._ghost_score_multiplier = 1

        self.maze = Maze()
        self.player = Player(
            start_col=PLAYER_START["col"],
            start_row=PLAYER_START["row"],
            maze=self.maze
        )
        self.ghosts = [
            Ghost(cfg["col"], cfg["row"], cfg["personality"], self.maze)
            for cfg in GHOST_CONFIGS
        ]
        self.hud = HUD(SCREEN_WIDTH)
        self.hud.init()

    def _power_duration(self) -> float:
        d = POWER_DURATION_BASE - (self.level - 1) * POWER_DURATION_DECREMENT
        return max(d, POWER_DURATION_MIN)

    def _ghost_speed(self) -> float:
        return GHOST_BASE_SPEED + (self.level - 1) * GHOST_SPEED_INCREMENT

    def _reset_level(self, next_level=False):
        if next_level:
            self.level += 1
        self.maze.reset()
        self.player.col = PLAYER_START["col"]
        self.player.row = PLAYER_START["row"]
        self.player.snap_to_grid()
        self.player.dx = 0
        self.player.dy = 0
        self.player.powered_up = False
        speed = self._ghost_speed()
        for ghost in self.ghosts:
            ghost.reset()
            ghost.speed = speed
        self._ghost_score_multiplier = 1
        self.state = GameState.PLAYING

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.PLAYING:
                    if event.key == pygame.K_RIGHT:
                        self.player.set_direction(1, 0)
                    elif event.key == pygame.K_LEFT:
                        self.player.set_direction(-1, 0)
                    elif event.key == pygame.K_UP:
                        self.player.set_direction(0, -1)
                    elif event.key == pygame.K_DOWN:
                        self.player.set_direction(0, 1)
                elif self.state in (GameState.GAME_OVER, GameState.LEVEL_COMPLETE):
                    if event.key == pygame.K_RETURN:
                        if self.state == GameState.GAME_OVER:
                            self._full_reset()
                        else:
                            self._reset_level(next_level=True)

    def _full_reset(self):
        self.level = 1
        self.player.lives = PLAYER_LIVES
        self.player.score = 0
        self._reset_level()

    def update(self, dt: float):
        if self.state == GameState.PLAYING:
            # Verificar se power-up foi coletado neste frame
            prev_powered = self.player.powered_up
            self.player.update(dt)

            # Se player acabou de coletar power-up, ativar modo scared nos ghosts
            if self.player.powered_up and not prev_powered:
                dur = self._power_duration()
                self.player.activate_power(dur)
                self._ghost_score_multiplier = 1
                for ghost in self.ghosts:
                    ghost.set_scared(dur)

            for ghost in self.ghosts:
                ghost.update(dt, self.player)
                if ghost.get_rect().colliderect(self.player.get_rect()):
                    if self.player.powered_up and ghost.scared:
                        # Come o Beagle
                        self.player.score += SCORE_GHOST_BASE * self._ghost_score_multiplier
                        self._ghost_score_multiplier *= 2
                        ghost.reset()
                        ghost.speed = self._ghost_speed()
                    elif not self.player.powered_up:
                        # Morre
                        self.player.die()
                        if self.player.is_dead():
                            self.state = GameState.GAME_OVER
                        else:
                            self.state = GameState.DYING
                            self._state_timer = 1.5
                        for g in self.ghosts:
                            g.reset()
                            g.speed = self._ghost_speed()
                        self._ghost_score_multiplier = 1

            if self.maze.all_collected():
                self.state = GameState.LEVEL_COMPLETE
                self._state_timer = 2.0

        elif self.state == GameState.DYING:
            self._state_timer -= dt
            if self._state_timer <= 0:
                self.state = GameState.PLAYING

        elif self.state == GameState.LEVEL_COMPLETE:
            self._state_timer -= dt
            if self._state_timer <= 0:
                self._reset_level(next_level=True)

    def draw(self):
        self.surface.fill(DARK_BLUE)
        self.maze.draw(self.surface)
        self.player.draw(self.surface)
        for ghost in self.ghosts:
            ghost.draw(self.surface)
        self.hud.draw(self.surface, self.player.score, self.player.lives, self.level)

        if self.state == GameState.LEVEL_COMPLETE:
            self.hud.draw_message(self.surface, "BOLA SALVA!", (200, 255, 100))
        elif self.state == GameState.GAME_OVER:
            self.hud.draw_message(self.surface, "APANHADO!", (255, 80, 80))
            sub = pygame.font.SysFont("monospace", 20).render(
                "ENTER para recomecar", True, (200, 200, 200))
            self.surface.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2,
                                    SCREEN_HEIGHT // 2 + 50))

        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
```

- [ ] **Step 2: Commit**

```bash
git add game.py
git commit -m "feat: game orchestration, state machine, collisions and progression"
```

---

### Task 7: Entry point

**Files:**
- Create: `main.py`

- [ ] **Step 1: Implementar main.py**

```python
# main.py
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, TITLE
from game import Game


def main():
    pygame.init()
    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    game = Game(screen)
    game.run()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Rodar o jogo para verificação visual**

```bash
python main.py
```
Esperado: janela abre, labirinto visível, Border Collie controlável com setas, Beagles se movendo, HUD com pontuação.

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "feat: main entry point — game is playable"
```

---

## Chunk 5: Assets e Polimento

### Task 8: Buscar/gerar sprites e integrar

**Files:**
- Create: `sprite_loader.py`

- [ ] **Step 1: Verificar OpenGameArt para sprites de cachorro**

Acessar: https://opengameart.org e buscar por "dog sprite" ou "beagle sprite" com licença CC0.

Se encontrar sprites adequados (32x32px, 4 direções):
- Baixar e salvar em `assets/sprites/border_collie/` e `assets/sprites/beagle/`
- Pular para Step 3.

Se não encontrar sprites ideais, usar fallback (pygame.draw já implementado — pular Task 8).

- [ ] **Step 2: Implementar sprite_loader.py**

```python
# sprite_loader.py
import os
import pygame
from settings import TILE_SIZE


def load_image(path: str, size=(TILE_SIZE, TILE_SIZE)) -> pygame.Surface:
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, size)


def load_player_sprites(base_dir="assets/sprites/border_collie") -> dict:
    """
    Retorna dict: {((dx,dy), frame): Surface}
    Espera arquivos: right_0.png, right_1.png, right_2.png,
                     left_0.png, ... up_0.png, ... down_0.png, ...
    """
    sprites = {}
    directions = {(1, 0): "right", (-1, 0): "left", (0, -1): "up", (0, 1): "down"}
    for (dx, dy), name in directions.items():
        for frame in range(3):
            path = os.path.join(base_dir, f"{name}_{frame}.png")
            if os.path.exists(path):
                sprites[((dx, dy), frame)] = load_image(path)
    return sprites


def load_ghost_sprites(personality_name: str,
                       base_dir="assets/sprites/beagle") -> dict:
    sprites = {}
    path = os.path.join(base_dir, f"{personality_name}_normal.png")
    scared_path = os.path.join(base_dir, "scared.png")
    if os.path.exists(path):
        sprites["normal"] = load_image(path)
    if os.path.exists(scared_path):
        sprites["scared"] = load_image(scared_path)
    return sprites
```

- [ ] **Step 3: Integrar sprites no main.py (opcional se não houver sprites)**

```python
# Adicionar em main.py após pygame.init():
from sprite_loader import load_player_sprites, load_ghost_sprites

player_sprites = load_player_sprites()
if player_sprites:
    game.player.load_sprites(player_sprites)

for ghost in game.ghosts:
    ghost_sprites = load_ghost_sprites(ghost.personality.value)
    if ghost_sprites:
        ghost.load_sprites(ghost_sprites)
```

- [ ] **Step 4: Commit**

```bash
git add sprite_loader.py assets/sprites/ main.py
git commit -m "feat: sprite loader with fallback to procedural drawing"
```

---

### Task 9: Testes de integração e verificação final

- [ ] **Step 1: Rodar todos os testes**

```bash
pytest tests/ -v
```
Esperado: todos passando.

- [ ] **Step 2: Jogar manualmente e verificar**

Checklist:
- [ ] Border Collie se move com setas
- [ ] Bolinhas de tênis somem ao ser coletadas
- [ ] Pontuação aumenta
- [ ] Power-up ativa modo turbo (Beagles ficam azuis)
- [ ] Beagle capturado em power mode dá pontos e volta ao centro
- [ ] Colisão com Beagle normal tira uma vida
- [ ] Game Over após 3 mortes — exibe "APANHADO!"
- [ ] Fase completa exibe "BOLA SALVA!" e avança
- [ ] Beagles ficam mais rápidos na fase 2+

- [ ] **Step 3: Push final para GitHub**

```bash
git push origin main
```

- [ ] **Step 4: Commit de fechamento**

```bash
git add .
git commit -m "feat: BORDEPAC v1.0 — Border Collie PAC-Man completo"
git push origin main
```

---

## Resumo dos Arquivos

| Arquivo | Responsabilidade |
|---------|-----------------|
| `settings.py` | Todas as constantes do jogo |
| `maze.py` | Grid do labirinto, colisões, coleta |
| `player.py` | Movimento, animação, vidas, poder |
| `ghost.py` | IA dos Beagles, modo scared |
| `hud.py` | Renderização de score/vidas/fase/mensagens |
| `game.py` | Loop principal, state machine, colisões globais |
| `main.py` | Entry point, inicialização pygame |
| `sprite_loader.py` | Carregamento de PNGs externos |
| `tests/test_maze.py` | Testes da lógica do labirinto |
| `tests/test_player.py` | Testes de movimento e mecânicas do player |
| `tests/test_ghost.py` | Testes de IA e comportamento dos Beagles |
