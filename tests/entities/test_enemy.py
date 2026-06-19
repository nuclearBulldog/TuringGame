import pytest
import pygame
import settings
from entities.enemy import Enemy

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
