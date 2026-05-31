import sys
import pygame

import settings
from states.base_state import BaseState
from ui.button import Button


class SummaryMenu(BaseState):

    def __init__(self, manager):
        super().__init__(manager)
        cx = settings.WIDTH // 2

        self.title = self.game.big_font.render('Summary', True, settings.WHITE)
        self.title_rect = self.title.get_rect(center=(cx, 110))

        self.buttons = [
            Button((cx - 130, 200, 260, 54), 'Main Menu', self.main_menu, self.game.font),
            Button((cx - 130, 270, 260, 54), 'Toggle Mute', self.toggle_mute, self.game.font),
            Button((cx - 130, 340, 260, 54), 'Quit', self.quit_game, self.game.font),
        ]

    def main_menu(self):
        # Local import avoids circular imports.
        from states.main_menu import MainMenu
        self.manager.change(MainMenu(self.manager))

    def toggle_mute(self):
        self.game.sound.toggle_mute()

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mouse_pos)

    def draw(self, screen):
        screen.fill((25, 32, 60))
        screen.blit(self.title, self.title_rect)
        subtitle = self.game.font.render(
            'Move: A/D   Jump: Space   Battle menu: Arrow keys + Enter', True, settings.WHITE
        )
        screen.blit(subtitle, subtitle.get_rect(center=(settings.WIDTH // 2, 155)))
        for button in self.buttons:
            button.draw(screen)
        muted_text = 'Muted: ON' if self.game.sound.muted else 'Muted: OFF'
        screen.blit(self.game.font.render(muted_text, True, settings.WHITE), (20, settings.HEIGHT - 34))

    def handle_events(self, events):
        for event in events:
            for button in self.buttons:
                button.handle_event(event)
