import pygame

from turing_game.states.battle import BattleState


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
        # Attributes read by BattleResultState when the battle transitions out
        self.player_won = False
        self.score = 0
        self.summary_items = []

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


def _key(key):
    return pygame.event.Event(pygame.KEYDOWN, {'key': key})


def test_battle_state_escape_returns_to_main_menu():
    manager = MockManager()
    state = BattleState(manager, system=MockBattleSystem())
    state.game = MockGame()

    state.handle_events([_key(pygame.K_ESCAPE)])

    assert manager.changed_state.__class__.__name__ == "MainMenu"


def test_battle_state_navigation_left_and_up():
    manager = MockManager()
    state = BattleState(manager, system=MockBattleSystem())
    state.game = MockGame()

    state.handle_events([_key(pygame.K_DOWN)])   # 0 -> 2
    assert state.selected_move == 2
    state.handle_events([_key(pygame.K_UP)])     # 2 -> 0 (up branch)
    assert state.selected_move == 0
    state.handle_events([_key(pygame.K_RIGHT)])  # 0 -> 1
    assert state.selected_move == 1
    state.handle_events([_key(pygame.K_LEFT)])   # 1 -> 0 (left/odd branch)
    assert state.selected_move == 0


def test_battle_state_ignores_moves_when_battle_over():
    manager = MockManager()
    system = MockBattleSystem()
    system.battle_over = True  # input past ESCAPE should be swallowed
    state = BattleState(manager, system=system)
    state.game = MockGame()

    state.handle_events([_key(pygame.K_RIGHT)])

    assert state.selected_move == 0  # selection unchanged


def test_battle_state_transitions_to_result_after_delay():
    manager = MockManager()
    system = MockBattleSystem()
    system.battle_over = True
    state = BattleState(manager, system=system)
    state.game = MockGame()

    # Below the finished_delay: no transition yet
    state.update(0.1)
    assert manager.changed_state is None

    # Crossing finished_delay (0.5) triggers the result screen exactly once
    state.update(0.5)
    assert state._result_shown is True
    assert manager.changed_state.__class__.__name__ == "BattleResultState"
