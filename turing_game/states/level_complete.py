from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from turing_game.engine.state_manager import StateManager
    from turing_game.world.level import Level

import pygame
import pygame_menu

from turing_game import settings
from turing_game.states.base_state import BaseState


class LevelCompleteState(BaseState):
    """Shown when the player reaches the goal flag.

    Holds the finished :class:`~world.level.Level` so future work (multi-level
    progression, campaign modules) can branch from ``next_level``. Today the
    only forward path starts a fresh randomly chosen level.
    """

    def __init__(self, manager: StateManager, level: Level | None = None) -> None:
        super().__init__(manager)
        self.level = level
        self.score = level.total_score if level is not None else 0
        self.cleared_count = len(level.cleared_encounters) if level is not None else 0

        self.base_font = settings.BASE_FONT

        theme = pygame_menu.themes.THEME_DEFAULT.copy()
        theme.background_color = (30, 120, 160)
        theme.title_background_color = (0, 0, 0, 100)
        theme.title_font_shadow = True
        theme.widget_padding = 15
        theme.widget_font = pygame.font.Font(self.base_font, 24)
        theme.title_font = pygame.font.Font(self.base_font, 32)

        self.menu = pygame_menu.Menu(
            'Level Complete',
            settings.WIDTH,
            settings.HEIGHT,
            theme=theme,
        )
        self.menu.add.label(
            'You reached the flag!',
            font_name=settings.BASE_FONT,
            font_color=settings.WHITE,
            font_size=44,
        )
        self.menu.add.label(
            f'Encounters cleared: {self.cleared_count}',
            font_name=settings.BASE_FONT,
            font_color=settings.WHITE,
            font_size=26,
        )
        self.menu.add.label(
            f'Score: {self.score}',
            font_name=settings.BASE_FONT,
            font_color=settings.WHITE,
            font_size=26,
        )
        self.menu.add.button('Play Again', self.next_level)
        self.menu.add.button('Main Menu', self.main_menu)

    def next_level(self) -> None:
        """Forward path after finishing a level.

        Seam for future multi-level progression; for now it starts a fresh
        randomly chosen level via ``play_again``.
        """
        self.play_again()

    def play_again(self) -> None:
        from turing_game.states.overworld import Overworld
        self.manager.change(Overworld(self.manager))

    def main_menu(self) -> None:
        from turing_game.states.main_menu import MainMenu
        self.manager.change(MainMenu(self.manager))

    def update(self, dt: float) -> None:
        pass

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        if self.menu.is_enabled():
            self.menu.update(events)

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.main_menu()

    def draw(self, screen: pygame.Surface) -> None:
        if self.menu.is_enabled():
            self.menu.draw(screen)
