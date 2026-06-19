import pygame
import pytest
from engine.camera import Camera
import settings

def test_camera_init():
    cam = Camera()
    assert cam.offset.x == 0
    assert cam.offset.y == 0

def test_camera_update():
    cam = Camera()
    # Mock settings to be predictable
    orig_width, orig_height, orig_lerp = settings.WIDTH, settings.HEIGHT, settings.CAMERA_LERP
    settings.WIDTH = 800
    settings.HEIGHT = 600
    settings.CAMERA_LERP = 1.0

    target = pygame.Rect(400, 300, 50, 50)
    # Center of target is (425, 325)
    # desired x = 425 - 400 = 25
    # desired y = 325 - 300 = 25
    cam.update(target)
    
    assert cam.offset.x == 25
    assert cam.offset.y == 25

    # Restore settings
    settings.WIDTH, settings.HEIGHT, settings.CAMERA_LERP = orig_width, orig_height, orig_lerp

def test_camera_apply():
    cam = Camera()
    cam.offset.x = 100
    cam.offset.y = 50

    rect = pygame.Rect(200, 100, 50, 50)
    new_rect = cam.apply_rect(rect)
    assert new_rect.x == 100
    assert new_rect.y == 50

    class MockObj:
        def __init__(self):
            self.rect = pygame.Rect(200, 100, 50, 50)

    obj = MockObj()
    new_rect2 = cam.apply(obj)
    assert new_rect2.x == 100
    assert new_rect2.y == 50
