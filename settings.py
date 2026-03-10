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
