import pygame

from turing_game import settings
from turing_game.states.main_menu import MainMenu


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


def test_main_menu_update_does_not_toggle_mute(monkeypatch):
    # Regression: mute must only toggle on a click event, never from per-frame update().
    manager = MockManager()
    menu = MainMenu(manager)
    menu.game = MockGame()

    # Simulate the mouse held down over the old sound-icon hitbox.
    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: (25, settings.HEIGHT - 35))
    monkeypatch.setattr(pygame.mouse, "get_pressed", lambda *args, **kwargs: (True, False, False))

    before = menu.game.sound_manager.muted
    menu.update(0.016)
    assert menu.game.sound_manager.muted == before


def test_sound_icon_is_fully_onscreen_and_clickable():
    """The clickable rect must match the drawn icon exactly.

    Regression: the icon was blitted at 48x48 but tested against a hardcoded
    20x20 rect anchored at HEIGHT-40, so most of the button ignored clicks and
    its bottom 8px hung off the screen.
    """
    menu = MainMenu(MockManager())
    menu.game = MockGame()
    rect = menu.sound_icon_rect

    assert rect.size == menu.icon_sound_on.get_size()
    assert rect.size == menu.icon_sound_off.get_size()
    assert rect.left >= 0 and rect.top >= 0
    assert rect.right <= settings.WIDTH
    assert rect.bottom <= settings.HEIGHT


def test_click_anywhere_on_sound_icon_toggles_mute():
    menu = MainMenu(MockManager())
    menu.game = MockGame()
    rect = menu.sound_icon_rect

    corners = [
        (rect.left, rect.top),
        (rect.right - 1, rect.top),
        (rect.left, rect.bottom - 1),
        (rect.right - 1, rect.bottom - 1),
        rect.center,
    ]
    for i, pos in enumerate(corners):
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos)
        menu.handle_events([event])
        assert menu.game.sound_manager.muted is (i % 2 == 0), f'no toggle at {pos}'
