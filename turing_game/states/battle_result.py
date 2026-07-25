from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from turing_game.engine.state_manager import StateManager

import pygame
import pygame_menu

from turing_game import settings
from turing_game.states.base_state import BaseState
from turing_game.systems.battle_system import BattleSystem


class BattleResultState(BaseState):
    def __init__(
        self,
        manager: StateManager,
        return_to_state: BaseState | None = None,
        system: BattleSystem | None = None,
    ) -> None:
        super().__init__(manager)
        self.return_to_state = return_to_state
        self.system = system if system else BattleSystem()

        self.base_font = settings.BASE_FONT

        self.win = self.system.player_won
        self.show_details = False

        # A win resumes the persistent level in place; a loss is terminal and
        # only offers a fresh start (matching the original behaviour).
        if self.win and self.return_to_state is not None:
            self.forward_label = 'Continue'
            self.forward_action = self.continue_level
        else:
            self.forward_label = 'Play Again'
            self.forward_action = self.play_again

        bg_colour = (30, 160, 60) if self.win else (200, 40, 40)

        theme = pygame_menu.themes.THEME_DEFAULT.copy()
        theme.background_color = bg_colour
        theme.title_background_color = (0, 0, 0, 100)
        theme.title_font_shadow = True
        theme.widget_padding = 15

        theme.widget_font = pygame.font.Font(self.base_font, 24)
        theme.title_font = pygame.font.Font(self.base_font, 32)

        selection_effect = pygame_menu.widgets.HighlightSelection(
            border_width=2,
            margin_x=16,
            margin_y=8,
        )

        selection_effect.set_color((255, 255, 255, 80))
        selection_effect.set_background_color((255, 255, 255, 30))

        theme.widget_selection_effect = selection_effect

        title_text = "You Win Good Job!" if self.win else "You Have Lost... Get Good"

        self.menu = pygame_menu.Menu(
            'Results',
            settings.WIDTH,
            settings.HEIGHT,
            theme=theme,
        )

        self.menu.add.label(
            title_text,
            font_name=settings.BASE_FONT,
            font_color=settings.WHITE,
            font_size=44,
        )
        self.menu.add.button('Details', self.toggle_details)
        self.menu.add.button(self.forward_label, self.forward_action)
        self.menu.add.button('Main Menu', self.main_menu)

    def toggle_details(self) -> None:
        self.show_details = not self.show_details

    def continue_level(self) -> None:
        # Resume the persistent overworld and retire the enemy just defeated.
        self.return_to_state.resolve_won_battle(self.system)
        self.manager.change(self.return_to_state)

    def play_again(self) -> None:
        from turing_game.states.overworld import Overworld
        # Starts a fresh, randomly chosen level.
        self.manager.change(Overworld(self.manager))

    def main_menu(self) -> None:
        from turing_game.states.main_menu import MainMenu
        self.manager.change(MainMenu(self.manager))

    def update(self, dt: float) -> None:
        pass

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        if self.show_details:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.show_details = False
                        return
            return

        if self.menu.is_enabled():
            self.menu.update(events)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.main_menu()
                elif event.key == pygame.K_RETURN:
                    if not self.menu.get_current().get_selected_widget():
                        self.forward_action()

    def draw(self, screen: pygame.Surface) -> None:
        result_font = pygame.font.Font(self.base_font, 24)
        if self.menu.is_enabled():
            self.menu.draw(screen)

        if self.show_details:
            overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            panel = pygame.Rect(80, 150, settings.WIDTH - 160, 300)
            pygame.draw.rect(screen, (245, 245, 250), panel, border_radius=15)
            pygame.draw.rect(screen, (20, 20, 20), panel, 4, border_radius=15)

            lines = self._build_detail_lines()
            y = panel.y + 25
            for line in lines:
                s = result_font.render(line, False, (20, 20, 20))
                screen.blit(s, (panel.x + 25, y))
                y += 30

            hint_surf = self.game.font.render("Press ESC to close", False, (150, 150, 150))
            hint_rect = hint_surf.get_rect(center=(settings.WIDTH // 2, panel.bottom - 20))
            screen.blit(hint_surf, hint_rect)

    def _build_detail_lines(self) -> list[str]:
        lines = ['Summary:']

        # If you have a list like system.summary_items = [("foo", True), ("bar", False)]
        if hasattr(self.system, "summary_items"):
            for name, ok in self.system.summary_items:
                mark = "Good" if ok else "BAD"
                lines.append(f"  {mark} {name}")

        if hasattr(self.system, "score"):
            lines.append(f"Points: {self.system.score}")

        # Add anything else you track (turns taken, damage, etc.)
        return lines
