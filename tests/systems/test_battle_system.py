import pytest
import json
from systems.battle_system import BattleSystem, Move

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
