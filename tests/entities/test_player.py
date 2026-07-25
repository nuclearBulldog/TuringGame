import pygame

from turing_game import settings
from turing_game.entities.player import Player


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


def _press(*keys):
    from collections import defaultdict

    def mock_get_pressed():
        pressed = defaultdict(bool)
        for key in keys:
            pressed[key] = True
        return pressed
    return mock_get_pressed


def test_player_moves_left(monkeypatch):
    monkeypatch.setattr(pygame.key, "get_pressed", _press(pygame.K_LEFT))

    player = Player(100, 100)
    player.update(0.1, [])

    assert player.vel.x == -settings.PLAYER_SPEED
    assert player.facing_right is False


def test_player_left_collision(monkeypatch):
    monkeypatch.setattr(pygame.key, "get_pressed", _press(pygame.K_a))

    player = Player(100, 100)
    player.vel.x = -100  # moving left

    # Wall flush against the player's left edge
    tile_left = MockTile(70, 100, 30, 50)
    player.update(0.1, [tile_left])

    assert player.rect.left == tile_left.rect.right


def test_player_ceiling_collision(monkeypatch):
    monkeypatch.setattr(pygame.key, "get_pressed", _press())

    player = Player(100, 100)
    # Strong upward velocity so it stays negative after gravity (1800 * 0.1 = 180)
    player.vel.y = -650

    # Ceiling sits in the player's upward path so the rects overlap after moving
    ceiling = MockTile(100, 40, 50, 40)
    player.update(0.1, [ceiling])

    assert player.rect.top == ceiling.rect.bottom
    assert player.vel.y == 0
    assert player.on_ground is False


def test_player_idle_animation_when_still(monkeypatch):
    monkeypatch.setattr(pygame.key, "get_pressed", _press())

    player = Player(100, 100)
    player.on_ground = True  # standing on the ground, no input
    player.vel.y = 0
    # Floor directly beneath keeps on_ground True through the update
    floor = MockTile(90, 140, 60, 20)
    player.update(0.1, [floor])

    assert player.animator.current == 'idle'


def test_player_draw_facing_left_runs(monkeypatch):
    monkeypatch.setattr(pygame.key, "get_pressed", _press())

    class MockCamera:
        offset = pygame.Vector2(5, 5)

    player = Player(100, 100)
    player.facing_right = False  # exercise the flip branch
    screen = pygame.Surface((400, 400))
    player.draw(screen, MockCamera())
