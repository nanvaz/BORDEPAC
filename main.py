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
