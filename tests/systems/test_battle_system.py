import json

import pytest
from systems.battle_system import BattleSystem


@pytest.fixture
def mock_encounter_data(tmp_path, monkeypatch):
    import settings
    # Create a temporary json file with encounter data
    encounters = {
        "test_encounter": {
            "enemy_name": "Test Enemy",
            "enemy_hp": 50,
            "enemy_max_hp": 50,
            "intro_message": "A wild test appears!",
            "moves": [
                {"name": "Attack", "damage": 20, "description": "Basic attack"},
                {"name": "Heal", "damage": -10, "description": "Heals HP"}
            ]
        }
    }

    # Mock settings.ENCOUNTER_DIR to tmp_path
    monkeypatch.setattr(settings, "ENCOUNTER_DIR", tmp_path)

    with open(tmp_path / "encounters.json", "w") as f:
        json.dump(encounters, f)

    return "test_encounter"

def test_battle_system_init(mock_encounter_data):
    system = BattleSystem(encounter_id=mock_encounter_data)

    assert system.enemy_name == "Test Enemy"
    assert system.enemy_hp == 50
    assert system.player_hp == 100
    assert len(system.moves) == 2
    assert system.moves[0].name == "Attack"
    assert system.turn == 'player'
    assert not system.battle_over

def test_battle_system_player_attack(mock_encounter_data):
    system = BattleSystem(encounter_id=mock_encounter_data)

    # Use Attack (index 0, 20 damage)
    system.player_use_move(0)

    assert system.enemy_hp == 30
    assert system.turn == 'enemy'
    assert "Attack" in system.moves_used

def test_battle_system_player_heal(mock_encounter_data):
    system = BattleSystem(encounter_id=mock_encounter_data)
    system.player_hp = 50 # manually reduce HP

    # Use Heal (index 1, -10 damage)
    system.player_use_move(1)

    assert system.player_hp == 60
    assert system.turn == 'enemy'

def test_battle_system_enemy_turn(mock_encounter_data):
    system = BattleSystem(encounter_id=mock_encounter_data)

    system.enemy_take_turn()

    assert system.player_hp < 100
    assert system.turn == 'player'

def test_battle_system_win(mock_encounter_data, monkeypatch):
    system = BattleSystem(encounter_id=mock_encounter_data)

    # Modify attack to one-shot
    system.moves[0].damage = 100

    system.player_use_move(0)

    assert system.enemy_hp == 0
    assert system.battle_over
    assert system.player_won
    assert system.score > 0


def test_battle_system_flawless_scores_higher_than_hurt_win(mock_encounter_data):
    # Regression: a flawless (100% HP) win must score higher than a hurt (>=50%) win.
    flawless = BattleSystem(encounter_id=mock_encounter_data)
    flawless.moves[0].damage = 100
    flawless.player_use_move(0)          # win at full HP

    hurt = BattleSystem(encounter_id=mock_encounter_data)
    hurt.moves[0].damage = 100
    hurt.player_hp = 50                   # win at half HP
    hurt.player_use_move(0)

    assert flawless.player_won and hurt.player_won
    assert flawless.score > hurt.score


def test_battle_system_flawless_bonus(mock_encounter_data):
    system = BattleSystem(encounter_id=mock_encounter_data)
    system.moves[0].damage = 100
    system.player_use_move(0)
    # base 100 (win) + 200 (flawless HP) + 200 (<=3 turns) == 500
    assert system.score == 500
    assert ("Flawless Victory (AMAZING 100%!)", True) in system.summary_items


def test_battle_system_hurt_win_bonus(mock_encounter_data):
    system = BattleSystem(encounter_id=mock_encounter_data)
    system.moves[0].damage = 100
    system.player_hp = 50
    system.player_use_move(0)
    # base 100 (win) + 50 (>=50% HP) + 200 (<=3 turns) == 350
    assert system.score == 350
    assert ("Not too bad (>=50%)", True) in system.summary_items


def test_battle_system_use_chatgpt_instant_loss(mock_encounter_data):
    # Regression: the "Use ChatGPT" move short-circuits to a loss with score 0.
    system = BattleSystem(encounter_id=mock_encounter_data)
    system.moves[0].name = "Use ChatGPT"
    system.player_use_move(0)

    assert system.player_won is False
    assert system.score == 0
    assert ("Caught by AI Detector", False) in system.summary_items


def test_battle_system_missing_file_raises(tmp_path, monkeypatch):
    import settings
    monkeypatch.setattr(settings, "ENCOUNTER_DIR", tmp_path)  # no encounters.json present
    with pytest.raises(FileNotFoundError):
        BattleSystem(encounter_id="test_encounter")


def test_battle_system_invalid_json_raises(tmp_path, monkeypatch):
    import settings
    monkeypatch.setattr(settings, "ENCOUNTER_DIR", tmp_path)
    (tmp_path / "encounters.json").write_text("{not valid json")
    with pytest.raises(ValueError):
        BattleSystem(encounter_id="test_encounter")
