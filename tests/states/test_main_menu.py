import pytest
import pygame
from states.main_menu import MainMenu

class MockManager:
    def __init__(self):
        self.changed_state = None
        self.game = MockGame()
    def change(self, state):
        self.changed_state = state

class MockSoundManager:
    def __init__(self):
        self.muted = False
    def toggle_mute(self):
        self.muted = not self.muted

class MockGame:
    def __init__(self):
        self.font = pygame.font.Font(None, 20)
        self.sound_manager = MockSoundManager()

def test_main_menu_init():
    manager = MockManager()
    menu = MainMenu(manager)
    menu.game = MockGame()
    
    assert len(menu.buttons) == 2

def test_main_menu_start_game():
    manager = MockManager()
    menu = MainMenu(manager)
    menu.game = MockGame()
    
    menu.start_game()
    assert manager.changed_state is not None
    assert manager.changed_state.__class__.__name__ == "Overworld"

def test_main_menu_mute_toggle():
    manager = MockManager()
    menu = MainMenu(manager)
    menu.game = MockGame()
    
    assert menu.game.sound_manager.muted is False
    menu.toggle_mute()
    assert menu.game.sound_manager.muted is True

def test_main_menu_quit(monkeypatch):
    import sys
    manager = MockManager()
    menu = MainMenu(manager)
    menu.game = MockGame()
    
    exited = False
    def mock_exit():
        nonlocal exited
        exited = True
        
    monkeypatch.setattr(sys, "exit", mock_exit)
    menu.quit_game()
    assert exited is True
