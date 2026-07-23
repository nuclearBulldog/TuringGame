import pygame
import settings
from engine.camera import Camera


def test_camera_init():
    cam = Camera()
    assert cam.offset.x == 0
    assert cam.offset.y == 0

def test_camera_update(monkeypatch):
    cam = Camera()
    # Mock settings to be predictable (monkeypatch auto-restores after the test,
    # even if an assertion fails, so no global state leaks into other tests).
    monkeypatch.setattr(settings, "WIDTH", 800)
    monkeypatch.setattr(settings, "HEIGHT", 600)
    monkeypatch.setattr(settings, "CAMERA_LERP", 1.0)

    target = pygame.Rect(400, 300, 50, 50)
    # Center of target is (425, 325)
    # desired x = 425 - 400 = 25
    # desired y = 325 - 300 = 25
    cam.update(target)

    assert cam.offset.x == 25
    assert cam.offset.y == 25

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
