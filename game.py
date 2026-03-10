# game.py
import pygame
import sys
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, DARK_BLUE,
    GHOST_BASE_SPEED, GHOST_SPEED_INCREMENT,
    POWER_DURATION_BASE, POWER_DURATION_DECREMENT, POWER_DURATION_MIN,
    SCORE_GHOST_BASE, PLAYER_LIVES,
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
    PLAYING       = "playing"
    DYING         = "dying"
    LEVEL_COMPLETE = "level_complete"
    GAME_OVER     = "game_over"


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
            maze=self.maze,
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

    def _full_reset(self):
        self.level = 1
        self.player.lives = PLAYER_LIVES
        self.player.score = 0
        self._reset_level()

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

    def update(self, dt: float):
        if self.state == GameState.PLAYING:
            prev_powered = self.player.powered_up
            self.player.update(dt)

            # If player just collected a power-up, sync duration and scare ghosts
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
                        self.player.score += SCORE_GHOST_BASE * self._ghost_score_multiplier
                        self._ghost_score_multiplier *= 2
                        ghost.reset()
                        ghost.speed = self._ghost_speed()
                    elif not self.player.powered_up:
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
                        break

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
