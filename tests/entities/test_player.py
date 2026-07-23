import pygame
import settings
from entities.player import Player


class MockTile:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)

def test_player_init():
    player = Player(100, 100)
    assert player.pos.x == 100
    assert player.pos.y == 100
    assert player.on_ground is False
    assert player.facing_right is True
    assert player.animator is not None

def test_player_gravity(monkeypatch):
    # Mock keys so player doesn't move horizontally or jump
    def mock_get_pressed():
        from collections import defaultdict
        return defaultdict(bool)
    monkeypatch.setattr(pygame.key, "get_pressed", mock_get_pressed)

    player = Player(100, 100)
    dt = 0.1
    player.update(dt, [])

    # Gravity should increase vel.y
    assert player.vel.y == settings.GRAVITY * dt
    # Pos y should increase
    assert player.pos.y > 100
    assert player.on_ground is False

def test_player_collision(monkeypatch):
    def mock_get_pressed():
        from collections import defaultdict
        keys = defaultdict(bool)
        keys[pygame.K_d] = True
        return keys
    monkeypatch.setattr(pygame.key, "get_pressed", mock_get_pressed)

    player = Player(100, 100)
    # Set velocity so player moves right and down
    player.vel.x = 100
    player.vel.y = 100

    # Place a solid tile directly to the right
    tile_right = MockTile(130, 100, 50, 50)
    # Place a solid tile directly below
    tile_bottom = MockTile(100, 140, 50, 50)

    # dt is small so we hit the objects
    player.update(0.1, [tile_right, tile_bottom])

    assert player.on_ground is True
    assert player.vel.y == 0
    assert player.rect.right == tile_right.rect.left
    assert player.rect.bottom == tile_bottom.rect.top

def test_player_jump(monkeypatch):
    def mock_get_pressed():
        from collections import defaultdict
        keys = defaultdict(bool)
        keys[pygame.K_SPACE] = True
        return keys
    monkeypatch.setattr(pygame.key, "get_pressed", mock_get_pressed)

    player = Player(100, 100)
    player.on_ground = True  # Must be on ground to jump
    player.update(0.1, [])

    # Jump velocity is applied, then gravity
    assert player.vel.y == settings.PLAYER_JUMP_VELOCITY + (settings.GRAVITY * 0.1)
    assert player.on_ground is False
