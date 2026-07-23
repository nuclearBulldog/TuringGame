import pygame
from states.battle_result import BattleResultState


class MockManager:
    def __init__(self):
        self.changed_state = None
        self.game = MockGame()
    def change(self, state):
        self.changed_state = state

class MockGame:
    def __init__(self):
        self.font = pygame.font.Font(None, 20)

class MockBattleSystem:
    def __init__(self, won=True):
        self.player_won = won
        self.score = 150
        self.summary_items = [("Defeated enemy", True), ("Took too much damage", False)]

def test_battle_result_init_win():
    # FR4: The system should display a end screen indicating if the user won or lost
    manager = MockManager()
    system = MockBattleSystem(won=True)
    state = BattleResultState(manager, system=system)
    state.game = MockGame()

    assert state.win is True
    # Verify title text includes "Win"
    assert any("Win" in w.get_title() for w in state.menu.get_widgets() if hasattr(w, 'get_title'))

def test_battle_result_init_loss():
    # FR4: The system should display a end screen indicating if the user won or lost
    manager = MockManager()
    system = MockBattleSystem(won=False)
    state = BattleResultState(manager, system=system)
    state.game = MockGame()

    assert state.win is False
    # Verify title text includes "Lost"
    assert any("Lost" in w.get_title() for w in state.menu.get_widgets() if hasattr(w, 'get_title'))

def test_battle_result_details():
    # FR5: The system should store the players decisions, in order to display feedback
    manager = MockManager()
    system = MockBattleSystem()
    state = BattleResultState(manager, system=system)
    state.game = MockGame()

    lines = state._build_detail_lines()
    assert "  Good Defeated enemy" in lines
    assert "  BAD Took too much damage" in lines
    assert "Points: 150" in lines

    assert state.show_details is False
    state.toggle_details()
    assert state.show_details is True

def test_battle_result_buttons():
    manager = MockManager()
    system = MockBattleSystem()
    state = BattleResultState(manager, system=system)
    state.game = MockGame()

    state.play_again()
    assert manager.changed_state.__class__.__name__ == "Overworld"

    state.main_menu()
    assert manager.changed_state.__class__.__name__ == "MainMenu"
