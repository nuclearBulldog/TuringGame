import pygame
from states.battle import BattleState


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

class MockBattleSystem:
    def __init__(self):
        self.turn = 'player'
        self.battle_over = False
        self.moves = [1, 2, 3, 4]
        self.used_move = None
        self.enemy_took_turn = False

    def player_use_move(self, idx):
        self.used_move = idx

    def enemy_take_turn(self):
        self.enemy_took_turn = True

def test_battle_state_init():
    manager = MockManager()
    system = MockBattleSystem()
    state = BattleState(manager, system=system)
    state.game = MockGame()

    assert state.selected_move == 0

def test_battle_state_handle_events_move_selection():
    manager = MockManager()
    system = MockBattleSystem()
    state = BattleState(manager, system=system)
    state.game = MockGame()

    # Mock events for arrow keys
    event_right = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RIGHT})
    state.handle_events([event_right])

    assert state.selected_move == 1

    event_down = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_DOWN})
    state.handle_events([event_down])

    assert state.selected_move == 3

def test_battle_state_handle_events_action():
    manager = MockManager()
    system = MockBattleSystem()
    state = BattleState(manager, system=system)
    state.game = MockGame()

    event_enter = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RETURN})
    state.handle_events([event_enter])

    assert system.used_move == 0

def test_battle_state_update_enemy_turn():
    manager = MockManager()
    system = MockBattleSystem()
    system.turn = 'enemy'
    state = BattleState(manager, system=system)
    state.game = MockGame()

    # Pass time to trigger enemy action
    state.update(1.0)
    assert system.enemy_took_turn is True
