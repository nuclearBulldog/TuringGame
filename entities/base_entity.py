# AI Generated BoilerPlate

import pygame


class BaseEntity:
    """Base class for world objects with position, velocity, and collision rect."""

    def __init__(self, x, y, w, h):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.rect = pygame.Rect(x, y, w, h)

    def sync_rect(self):
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
