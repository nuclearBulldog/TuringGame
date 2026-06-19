import os
import sys
import pytest

# Add turing-game to sys.path so we can import from it easily in tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../turing-game')))

# Set dummy drivers for headless testing BEFORE pygame is imported
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

@pytest.fixture(autouse=True)
def mock_pygame(monkeypatch):
    """
    Initialize and tear down pygame for every test to avoid state bleeding.
    Also mocks pygame-menu if needed.
    """
    pygame.init()
    
    # Initialize a dummy display mode so convert_alpha() works
    import settings
    pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))

    # Mock font.Font so we don't need actual font files to run tests
    class MockFont:
        def __init__(self, *args, **kwargs):
            pass
        def render(self, text, antialias, color, background=None):
            return pygame.Surface((10, 10), pygame.SRCALPHA)
        def size(self, text):
            return (10, 10)

    monkeypatch.setattr(pygame.font, "Font", MockFont)
    monkeypatch.setattr(pygame.font, "SysFont", MockFont)
    
    # Disable pygame_menu font assertion so it accepts MockFont
    import pygame_menu
    if hasattr(pygame_menu, "themes"):
        monkeypatch.setattr(pygame_menu.themes, "assert_font", lambda f: None)
    if hasattr(pygame_menu, "font"):
        monkeypatch.setattr(pygame_menu.font, "assert_font", lambda f: None)
    try:
        import pygame_menu._widgetmanager
        monkeypatch.setattr(pygame_menu._widgetmanager, "assert_font", lambda f: None)
    except:
        pass
    try:
        import pygame_menu.widgets.core.widget
        monkeypatch.setattr(pygame_menu.widgets.core.widget, "assert_font", lambda f: None)
    except:
        pass
    
    yield
    pygame.quit()
