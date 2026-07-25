import json

import pytest

from turing_game.world.tilemap import EnemySpawn, TileMap


@pytest.fixture(autouse=True)
def hermetic_encounters(tmp_path, monkeypatch):
    # TileMap resolves enemy spawn tiles through the encounter database, so give
    # every test a small, controlled one instead of the shipped file.
    from turing_game import settings
    database = {
        "report_due": {
            "spawn_tile": 3,
            "enemy_name": "Report Due",
            "enemy_hp": 10,
            "enemy_max_hp": 10,
            "intro_message": "x",
            "moves": [{"name": "Study", "damage": 5, "description": "y"}],
        }
    }
    monkeypatch.setattr(settings, "ENCOUNTER_DIR", tmp_path)
    (tmp_path / "encounters.json").write_text(json.dumps(database))


def _write_level(tmp_path):
    # tile codes: 0/1 solid, 2 player spawn, 3 encounter spawn (report_due),
    # 4 goal, -1 empty
    rows = [
        [-1, -1, -1, -1],
        [-1, 2, 3, 4],
        [0, 0, 0, 0],
    ]
    path = tmp_path / "level.csv"
    path.write_text("\n".join(",".join(str(code) for code in row) for row in rows))
    return path


def test_tilemap_tiles_scaled_to_tile_size(tmp_path):
    # Regression: scale() result was discarded, leaving tiles unscaled.
    tilemap = TileMap(_write_level(tmp_path))
    assert tilemap.dirt_img.get_size() == (tilemap.tile_size, tilemap.tile_size)
    assert tilemap.grass_img.get_size() == (tilemap.tile_size, tilemap.tile_size)


def test_tilemap_parses_spawns(tmp_path):
    tilemap = TileMap(_write_level(tmp_path))
    ts = tilemap.tile_size
    assert tilemap.player_spawn == (1 * ts, 1 * ts)
    assert EnemySpawn(2 * ts, 1 * ts, "report_due") in tilemap.enemy_spawns


def test_tilemap_binds_encounter_id_to_spawn_tile(tmp_path):
    tilemap = TileMap(_write_level(tmp_path))
    assert len(tilemap.enemy_spawns) == 1
    assert tilemap.enemy_spawns[0].encounter_id == "report_due"


def test_tilemap_builds_goal_rect(tmp_path):
    tilemap = TileMap(_write_level(tmp_path))
    ts = tilemap.tile_size
    assert tilemap.goal_rect is not None
    assert tilemap.goal_rect.topleft == (3 * ts, 1 * ts)
    assert tilemap.goal_rect.size == (ts, ts)


def test_tilemap_without_goal_has_none(tmp_path):
    rows = [[-1, 2, 3], [0, 0, 0]]
    path = tmp_path / "nogoal.csv"
    path.write_text("\n".join(",".join(str(c) for c in row) for row in rows))
    tilemap = TileMap(path)
    assert tilemap.goal_rect is None


def test_tilemap_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        TileMap(tmp_path / "does_not_exist.csv")
