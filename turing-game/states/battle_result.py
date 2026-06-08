import pygame
import pygame_menu

import settings
from states.base_state import BaseState
from systems.battle_system import BattleSystem

class BattleResultState(BaseState):
    def __init__(self, manager, return_to_state=None, system = None):
        super().__init__(manager)
        self.return_to_state = return_to_state
        self.system = system if system else BattleSystem()

        self.base_font = settings.BASE_FONT
        self.title_font = pygame.font.Font()

        self.win = self.system.player_won
        self.show_details = False

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



        self.menu.center_content()

        self.menu.add.label(title_text, font_name=settings.BASE_FONT, font_color=settings.WHITE, font_size=44)
        self.menu.add.button('Details', self.toggle_details)
        self.menu.add.button('Play Again', self.play_again)
        self.menu.add.button('Main Menu', self.main_menu)

    def toggle_details(self):
        self.show_details = not self.show_details

    def play_again(self):
        from states.overworld import Overworld
        # Later: inject a generator or level ID here
        self.manager.change(Overworld(self.manager))

    def main_menu(self):
        from states.main_menu import MainMenu
        self.manager.change(MainMenu(self.manager))

    def update(self, dt):
        pass

    def handle_events(self, events):
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
                        self.play_again()

    def draw(self, screen):
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

    def _build_detail_lines(self):
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
