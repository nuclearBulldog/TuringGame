import pygame
import pytest
from world.level import Level
from world.tilemap import EnemySpawn


class MockTileMap:
    def __init__(self, path):
        self.player_spawn = (64, 48)
        self.enemy_spawns = [
            EnemySpawn(200, 48, 'report_due'),
            EnemySpawn(400, 48, 'deepfake_classmate'),
        ]
        self.tiles = []
        self.goal_rect = pygame.Rect(500, 48, 16, 16)


@pytest.fixture
def mock_tilemap(monkeypatch):
    monkeypatch.setattr('world.level.TileMap', MockTileMap)


def test_level_builds_player_and_enemies(mock_tilemap):
    level = Level('dummy')
    assert level.player.pos.x == 64
    assert len(level.enemies) == 2
    assert level.enemies[0].encounter_id == 'report_due'
    assert level.cleared_encounters == set()
    assert level.total_score == 0


def test_level_clear_encounter_removes_and_records(mock_tilemap):
    level = Level('dummy')
    enemy = level.enemies[0]
    level.clear_encounter(enemy, score=150)
    assert enemy not in level.enemies
    assert 'report_due' in level.cleared_encounters
    assert level.total_score == 150


def test_level_clear_encounter_is_idempotent(mock_tilemap):
    # Resuming twice (or a stray double-call) must not double-count or error.
    level = Level('dummy')
    enemy = level.enemies[0]
    level.clear_encounter(enemy, score=150)
    level.clear_encounter(enemy, score=150)
    assert level.total_score == 150
    assert len(level.enemies) == 1


def test_level_load_random_picks_from_level_dir(monkeypatch, tmp_path, mock_tilemap):
    import settings
    monkeypatch.setattr(settings, 'LEVEL_DIR', tmp_path)
    for name in ['level1.csv', 'level2.csv', 'level3.csv']:
        (tmp_path / name).write_text('x')

    class StubRng:
        def __init__(self):
            self.seen = None

        def choice(self, seq):
            self.seen = list(seq)
            return self.seen[0]

    rng = StubRng()
    level = Level.load_random(rng=rng)
    assert level is not None
    assert len(rng.seen) == 3  # all three level*.csv files were candidates
