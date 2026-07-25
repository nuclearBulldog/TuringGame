import pygame

from turing_game import settings
from turing_game.entities.enemy import Enemy


class MockPlayer:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 10, 10)


class MockTile:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)


def test_enemy_init():
    enemy = Enemy(150, 100, 50)
    assert enemy.patrol_min_x == 100
    assert enemy.patrol_max_x == 200
    assert enemy.direction == 1
    assert enemy.state == 'patrol'
    # Defaults to the original report_due encounter when unspecified.
    assert enemy.encounter_id == 'report_due'


def test_enemy_binds_encounter_id():
    enemy = Enemy(150, 100, 50, encounter_id='deepfake_classmate')
    assert enemy.encounter_id == 'deepfake_classmate'
    # patrol_distance stays positional so existing call sites keep working.
    assert enemy.patrol_min_x == 100


def test_enemy_patrol():
    enemy = Enemy(150, 100, 50)
    player = MockPlayer(500, 100)  # Far away

    enemy.update(0.1, player, [])
    assert enemy.state == 'patrol'
    # Should move right
    assert enemy.vel.x == settings.ENEMY_SPEED
    assert enemy.pos.x > 150

    # Force to edge of patrol
    enemy.rect.x = 205
    enemy.update(0.1, player, [])
    assert enemy.direction == -1


def test_enemy_chase():
    enemy = Enemy(150, 100, 50)
    player = MockPlayer(170, 100)  # Within detection radius (200)

    enemy.update(0.1, player, [])
    assert enemy.state == 'chase'
    # Player is to the right, should chase right
    assert enemy.direction == 1
    assert enemy.vel.x == settings.ENEMY_SPEED

    player.rect.centerx = 100  # Move player to the left
    enemy.update(0.1, player, [])
    assert enemy.direction == -1
    assert enemy.vel.x == -settings.ENEMY_SPEED


def test_enemy_collision():
    enemy = Enemy(150, 100, 50)
    player = MockPlayer(500, 100)  # Far away
    enemy.vel.x = settings.ENEMY_SPEED

    # Place wall to the right
    wall = MockTile(180, 100, 50, 50)
    enemy.update(0.1, player, [wall])

    # Should hit wall and reverse direction
    assert enemy.rect.right == wall.rect.left
    assert enemy.direction == -1


def test_enemy_patrol_left_edge_reverses():
    enemy = Enemy(150, 100, 50)  # patrol_min_x == 100
    player = MockPlayer(900, 100)  # far away -> patrol
    enemy.direction = -1
    enemy.rect.x = 90  # at/under the left patrol bound

    enemy.update(0.1, player, [])
    assert enemy.direction == 1


def test_enemy_left_collision_reverses():
    enemy = Enemy(300, 100, 200)  # patrol range 100..500, so 300 is mid-patrol
    player = MockPlayer(900, 100)  # far away -> patrol
    enemy.direction = -1  # patrol drives vel.x negative

    wall = MockTile(270, 100, 30, 60)  # right edge flush at x=300
    enemy.update(0.1, player, [wall])

    assert enemy.rect.left == wall.rect.right
    assert enemy.direction == 1


def test_enemy_ground_collision():
    enemy = Enemy(150, 100, 50)
    player = MockPlayer(900, 100)  # far away

    floor = MockTile(140, 140, 60, 20)  # top at y=140, beneath the enemy
    enemy.update(0.1, player, [floor])

    assert enemy.on_ground is True
    assert enemy.vel.y == 0
    assert enemy.rect.bottom == floor.rect.top


def test_enemy_ceiling_collision():
    enemy = Enemy(150, 100, 50)
    player = MockPlayer(900, 100)  # far away
    enemy.vel.y = -650  # strong upward velocity, survives gravity

    ceiling = MockTile(120, 20, 90, 40)  # bottom at y=60, in the upward path
    enemy.update(0.1, player, [ceiling])

    assert enemy.rect.top == ceiling.rect.bottom
    assert enemy.vel.y == 0
    assert enemy.on_ground is False


def test_enemy_draw_runs_in_both_states():
    class MockCamera:
        offset = pygame.Vector2(10, 10)

    enemy = Enemy(150, 100, 50)
    enemy.direction = -1  # exercise the horizontal flip branch
    screen = pygame.Surface((400, 400))

    enemy.state = 'patrol'  # red marker branch
    enemy.draw(screen, MockCamera())
    enemy.state = 'chase'  # yellow marker branch
    enemy.draw(screen, MockCamera())
