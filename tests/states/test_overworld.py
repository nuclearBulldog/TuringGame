import pytest
import pygame
from states.overworld import Overworld
import settings

class MockManager:
    def __init__(self):
        self.changed_state = None
        self.game = MockGame()
    def change(self, state):
        self.changed_state = state

class MockGame:
    def __init__(self):
        self.font = pygame.font.Font(None, 20)
        self.big_font = pygame.font.Font(None, 32)

class MockTileMap:
    def __init__(self, path):
        self.player_spawn = (100, 100)
        self.enemy_spawns = [(300, 100)]
        self.tiles = []
    def draw(self, screen, camera):
        pass

def test_overworld_init(monkeypatch):
    monkeypatch.setattr("states.overworld.TileMap", MockTileMap)
    
    manager = MockManager()
    state = Overworld(manager)
    state.game = MockGame()
    
    assert state.player.pos.x == 100
    assert len(state.enemies) == 1
    assert state.enemies[0].pos.x == 300

def test_overworld_enemy_collision_starts_battle(monkeypatch):
    monkeypatch.setattr("states.overworld.TileMap", MockTileMap)
    
    manager = MockManager()
    state = Overworld(manager)
    state.game = MockGame()
    
    # Move player into enemy
    state.player.rect.x = 300
    state.player.rect.y = 100
    state.player.pos.x = 300
    state.player.pos.y = 100
    
    state.update(0.1)
    
    assert state._battle_started is True
    assert manager.changed_state is not None
    assert manager.changed_state.__class__.__name__ == "BattleState"
