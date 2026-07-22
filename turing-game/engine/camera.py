import pygame
import settings


class Camera:
    """Tracks the player and converts world coordinates into screen coordinates."""

    def __init__(self):
        self.offset = pygame.Vector2(0, 0)

    def update(self, target_rect):
        desired_x = target_rect.centerx - settings.WIDTH / 2
        desired_y = target_rect.centery - settings.HEIGHT / 2
        self.offset.x += (desired_x - self.offset.x) * settings.CAMERA_LERP
        self.offset.y += (desired_y - self.offset.y) * settings.CAMERA_LERP
        self.offset.x = max(0, self.offset.x)
        self.offset.y = max(0, self.offset.y)

    def apply_rect(self, rect):
        return rect.move(-int(self.offset.x), -int(self.offset.y))

    def apply(self, obj):
        rect = obj.rect if hasattr(obj, "rect") else obj
        return rect.move(-int(self.offset.x), -int(self.offset.y))
