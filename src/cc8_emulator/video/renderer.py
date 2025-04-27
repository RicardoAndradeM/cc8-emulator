import pygame
from pygame.surface import Surface

class Renderer:

    def __init__(self, width: int, height: int, scale: int):
        pygame.init()
        self.width = width
        self.height = height
        self.scale = scale
        self.screen = pygame.display.set_mode((self.width * self.scale, self.height * self.scale))
        self.clock = pygame.time.Clock()

    def renderFrame(self, frame: Surface):
        self.screen.blit(frame,(0,0))
        pygame.display.flip()

    def tick(self, framerate: int):
        self.clock.tick(framerate)