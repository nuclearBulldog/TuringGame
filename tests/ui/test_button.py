import pygame
from ui.button import Button


def make_button(callback=None):
    font = pygame.font.Font(None, 20)
    return Button((10, 10, 100, 40), "Play", callback or (lambda: None), font)


def test_button_init():
    button = make_button()
    assert button.rect == pygame.Rect(10, 10, 100, 40)
    assert button.text == "Play"
    assert button.hovered is False


def test_button_update_sets_hover_inside():
    button = make_button()
    button.update((50, 30))  # inside the rect
    assert button.hovered is True


def test_button_update_clears_hover_outside():
    button = make_button()
    button.hovered = True
    button.update((500, 500))  # outside the rect
    assert button.hovered is False


def test_button_click_inside_fires_callback():
    clicks = []
    button = make_button(callback=lambda: clicks.append(True))
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (50, 30)})
    button.handle_event(event)
    assert clicks == [True]


def test_button_click_outside_does_not_fire():
    clicks = []
    button = make_button(callback=lambda: clicks.append(True))
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (500, 500)})
    button.handle_event(event)
    assert clicks == []


def test_button_right_click_ignored():
    clicks = []
    button = make_button(callback=lambda: clicks.append(True))
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 3, 'pos': (50, 30)})
    button.handle_event(event)
    assert clicks == []


def test_button_draw_runs_without_error():
    screen = pygame.Surface((200, 100))
    button = make_button()
    button.hovered = True  # exercise the hovered fill branch
    button.draw(screen)
    button.hovered = False  # exercise the default fill branch
    button.draw(screen)
