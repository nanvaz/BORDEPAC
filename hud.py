# hud.py
import pygame
from settings import SCREEN_WIDTH, HUD_COLOR, WHITE, DOT_COLOR

HUD_HEIGHT = 40
FONT_SIZE = 24


class HUD:
    def __init__(self, screen_width: int):
        self.screen_width = screen_width
        self._font = None

    def init(self):
        self._font = pygame.font.SysFont("monospace", FONT_SIZE, bold=True)

    def draw(self, surface: pygame.Surface, score: int, lives: int, level: int):
        y = surface.get_height() - HUD_HEIGHT
        pygame.draw.rect(surface, (0, 0, 20),
                         pygame.Rect(0, y, self.screen_width, HUD_HEIGHT))

        score_surf = self._font.render(f"SCORE: {score:05d}", True, HUD_COLOR)
        surface.blit(score_surf, (10, y + 8))

        level_surf = self._font.render(f"FASE {level}", True, HUD_COLOR)
        lw = level_surf.get_width()
        surface.blit(level_surf, (self.screen_width // 2 - lw // 2, y + 8))

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
