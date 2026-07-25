import pygame


class BaseEntity:
    """Base class for world objects with position, velocity, and collision rect."""

    def __init__(self, x: float, y: float, w: int, h: int) -> None:
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.rect = pygame.Rect(x, y, w, h)

    def sync_rect(self) -> None:
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
