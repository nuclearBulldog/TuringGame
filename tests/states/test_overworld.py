import pygame
import pytest

from turing_game.states.overworld import Overworld
from turing_game.world.level import Level
from turing_game.world.tilemap import EnemySpawn


class MockManager:
    def __init__(self):
        self.changed_state = None
        self.game = MockGame()

    def change(self, state):
        self.changed_state = state


class MockSoundManager:
    muted = False

    def toggle_mute(self):
        self.muted = not self.muted


class MockGame:
    def __init__(self):
        self.font = pygame.font.Font(None, 20)
        self.big_font = pygame.font.Font(None, 32)
        self.sound_manager = MockSoundManager()


class MockTileMap:
    def __init__(self, path):
        self.player_spawn = (100, 100)
        self.enemy_spawns = [EnemySpawn(300, 100, 'report_due')]
        self.tiles = []
        self.goal_rect = pygame.Rect(600, 100, 16, 16)

    def draw(self, screen, camera):
        pass


@pytest.fixture
def level(monkeypatch):
    monkeypatch.setattr('turing_game.world.level.TileMap', MockTileMap)
    return Level('dummy')


def _overlap(player, rect):
    player.rect.topleft = rect.topleft
    player.pos.xy = (rect.x, rect.y)


def test_overworld_init(level):
    manager = MockManager()
    state = Overworld(manager, level=level)

    assert state.player.pos.x == 100
    assert len(state.enemies) == 1
    assert state.enemies[0].pos.x == 300


def test_overworld_enemy_collision_starts_bound_battle(level):
    manager = MockManager()
    state = Overworld(manager, level=level)
    state._grace_timer = 0.0  # skip the resume grace window

    _overlap(state.player, state.enemies[0].rect)
    state.update(0.1)

    assert state._battle_started is True
    battle = manager.changed_state
    assert battle.__class__.__name__ == "BattleState"
    # The battle resumes THIS overworld (persistent state), and is bound to the
    # enemy's encounter.
    assert battle.return_to_state is state
    assert battle.system.enemy_name == "Report Due"


def test_overworld_grace_blocks_immediate_recollision(level):
    # On resume the player stands where the enemy died; the grace window must
    # stop a fresh battle from firing on frame one.
    manager = MockManager()
    state = Overworld(manager, level=level)  # __init__ arms the grace timer

    _overlap(state.player, state.enemies[0].rect)
    state.update(0.1)

    assert state._battle_started is False
    assert manager.changed_state is None


def test_overworld_reaching_goal_transitions_to_level_complete(level):
    manager = MockManager()
    state = Overworld(manager, level=level)
    state._grace_timer = 0.0
    state.level.enemies.clear()  # clear path to the flag

    _overlap(state.player, state.tilemap.goal_rect)
    state.update(0.016)

    assert manager.changed_state.__class__.__name__ == "LevelCompleteState"


def test_overworld_win_resume_removes_enemy_permanently(level):
    manager = MockManager()
    state = Overworld(manager, level=level)
    state._grace_timer = 0.0
    enemy = state.enemies[0]

    _overlap(state.player, enemy.rect)
    state.update(0.1)  # starts the battle, records the pending enemy
    assert state._pending_enemy is enemy

    class WonSystem:
        score = 250

    state.resolve_won_battle(WonSystem())

    assert enemy not in state.enemies
    assert 'report_due' in state.level.cleared_encounters
    assert state.level.total_score == 250
    # Re-entering the overworld must not resurrect the defeated enemy.
    state.on_enter()
    assert enemy not in state.enemies
