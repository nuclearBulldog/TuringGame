import os

import pytest

# Set dummy drivers for headless testing BEFORE pygame is imported
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame  # noqa: E402  (must follow the SDL driver env vars above)

# Captured before mock_pygame swaps in MockFont, so tests that need genuine glyph
# metrics can still get them. See the real_font fixture.
_REAL_FONT = pygame.font.Font


@pytest.fixture
def real_font():
    """The genuine ``pygame.font.Font``, unaffected by the MockFont patch.

    Text-layout assertions need real metrics: MockFont reports 10x10 for every
    string, which makes any wrapping or fitting check vacuous.
    """
    return _REAL_FONT


@pytest.fixture(autouse=True)
def mock_pygame(monkeypatch):
    """
    Initialize and tear down pygame for every test to avoid state bleeding.
    Also mocks pygame-menu if needed.
    """
    pygame.init()

    # Initialize a dummy display mode so convert_alpha() works
    from turing_game import settings
    pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))

    # Mock font.Font so we don't need actual font files to run tests
    class MockFont:
        def __init__(self, *args, **kwargs):
            pass

        def render(self, text, antialias, color, background=None):
            return pygame.Surface((10, 10), pygame.SRCALPHA)

        def size(self, text):
            return (10, 10)

        def get_linesize(self):
            return 12

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
    except Exception:
        pass
    try:
        import pygame_menu.widgets.core.widget
        monkeypatch.setattr(pygame_menu.widgets.core.widget, "assert_font", lambda f: None)
    except Exception:
        pass

    yield
    pygame.quit()
