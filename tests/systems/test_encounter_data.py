import json

import pytest

from turing_game.systems import encounter_data


@pytest.fixture
def encounter_file(tmp_path, monkeypatch):
    from turing_game import settings
    database = {
        "report_due": {
            "spawn_tile": 3,
            "enemy_name": "Report Due",
            "enemy_hp": 140,
            "enemy_max_hp": 140,
            "intro_message": "Uh oh",
            "moves": [{"name": "Study", "damage": 25, "description": "x"}],
        },
        "deepfake": {
            "spawn_tile": 5,
            "enemy_name": "Deepfake",
            "enemy_hp": 100,
            "enemy_max_hp": 100,
            "intro_message": "Hmm",
            "moves": [{"name": "Report it", "damage": 40, "description": "y"}],
        },
        "no_tile": {
            "enemy_name": "Unreachable",
            "enemy_hp": 10,
            "enemy_max_hp": 10,
            "intro_message": "z",
            "moves": [{"name": "Poke", "damage": 5, "description": "w"}],
        },
    }
    monkeypatch.setattr(settings, "ENCOUNTER_DIR", tmp_path)
    (tmp_path / "encounters.json").write_text(json.dumps(database))
    return database


def test_load_encounters_returns_database(encounter_file):
    data = encounter_data.load_encounters()
    assert set(data) == {"report_due", "deepfake", "no_tile"}
    assert data["report_due"]["enemy_name"] == "Report Due"


def test_load_encounters_missing_file_raises(tmp_path, monkeypatch):
    from turing_game import settings
    monkeypatch.setattr(settings, "ENCOUNTER_DIR", tmp_path)
    with pytest.raises(FileNotFoundError):
        encounter_data.load_encounters()


def test_load_encounters_invalid_json_raises(tmp_path, monkeypatch):
    from turing_game import settings
    monkeypatch.setattr(settings, "ENCOUNTER_DIR", tmp_path)
    (tmp_path / "encounters.json").write_text("{not valid json")
    with pytest.raises(ValueError):
        encounter_data.load_encounters()


def test_spawn_tile_map_only_includes_declared_tiles(encounter_file):
    mapping = encounter_data.spawn_tile_map()
    assert mapping == {3: "report_due", 5: "deepfake"}


def test_spawn_tile_map_accepts_preloaded_database(encounter_file):
    database = encounter_data.load_encounters()
    mapping = encounter_data.spawn_tile_map(database)
    assert mapping[3] == "report_due"
    assert 5 in mapping
