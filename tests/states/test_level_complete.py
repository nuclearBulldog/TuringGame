import pygame
from states.level_complete import LevelCompleteState


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


class MockLevel:
    def __init__(self):
        self.total_score = 350
        self.cleared_encounters = {'report_due', 'deepfake_classmate'}


def test_level_complete_reports_level_score():
    manager = MockManager()
    state = LevelCompleteState(manager, level=MockLevel())
    state.game = MockGame()
    assert state.score == 350
    assert state.cleared_count == 2


def test_level_complete_play_again_starts_overworld():
    manager = MockManager()
    state = LevelCompleteState(manager, level=MockLevel())
    state.game = MockGame()

    state.play_again()
    assert manager.changed_state.__class__.__name__ == "Overworld"


def test_level_complete_main_menu():
    manager = MockManager()
    state = LevelCompleteState(manager, level=MockLevel())
    state.game = MockGame()

    state.main_menu()
    assert manager.changed_state.__class__.__name__ == "MainMenu"
