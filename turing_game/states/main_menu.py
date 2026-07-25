from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from turing_game.engine.state_manager import StateManager

import sys

import pygame

from turing_game import settings
from turing_game.states.base_state import BaseState
from turing_game.ui.image_button import ImageButton

ASSETS_DIR = settings.ASSETS_DIR
SCALE_FACTOR = 3.0


class MainMenu(BaseState):

    # Gap between the sound icon and the bottom-left corner of the screen.
    ICON_MARGIN = 20

    def __init__(self, manager: StateManager) -> None:
        super().__init__(manager)
        cx = settings.WIDTH // 2

        self.sprite_sheet = pygame.image.load(ASSETS_DIR / "ui_sheet.png").convert_alpha()

        self.SCALE_FACTOR = SCALE_FACTOR

        # ( (x, y, width, height) )
        rect_logo = (0, 192, 192, 64)  # "TURING GAME" banner
        rect_menu = (0, 48, 128, 144)  # blue menu that holds the buttons

        rect_play_normal = (128, 160, 64, 32)  # green play button with dark arrow
        rect_play_hover = (128, 128, 64, 32)  # green play button with light arrow
        rect_quit_normal = (192, 160, 64, 32)  # red quit button with closed door
        rect_quit_hover = (192, 128, 64, 32)  # red quit button with open door

        rect_sound_on = (192, 208, 16, 16)  # speaker icon
        rect_sound_off = (208, 208, 16, 16)  # speaker icon with red slash

        orig_logo = self.sprite_sheet.subsurface(rect_logo)
        orig_menu = self.sprite_sheet.subsurface(rect_menu)
        orig_img_play_normal = self.sprite_sheet.subsurface(rect_play_normal)
        orig_img_play_hover = self.sprite_sheet.subsurface(rect_play_hover)
        orig_img_quit_normal = self.sprite_sheet.subsurface(rect_quit_normal)
        orig_img_quit_hover = self.sprite_sheet.subsurface(rect_quit_hover)

        # scaling
        self.logo = pygame.transform.scale_by(orig_logo, self.SCALE_FACTOR)
        self.menu = pygame.transform.scale_by(orig_menu, self.SCALE_FACTOR)
        self.img_play_normal = pygame.transform.scale_by(orig_img_play_normal, self.SCALE_FACTOR)
        self.img_play_hover = pygame.transform.scale_by(orig_img_play_hover, self.SCALE_FACTOR)
        self.img_quit_normal = pygame.transform.scale_by(orig_img_quit_normal, self.SCALE_FACTOR)
        self.img_quit_hover = pygame.transform.scale_by(orig_img_quit_hover, self.SCALE_FACTOR)

        self.orig_icon_sound_on = self.sprite_sheet.subsurface(rect_sound_on)
        self.orig_icon_sound_off = self.sprite_sheet.subsurface(rect_sound_off)
        self.icon_sound_on = pygame.transform.scale_by(self.orig_icon_sound_on, self.SCALE_FACTOR)
        self.icon_sound_off = pygame.transform.scale_by(self.orig_icon_sound_off, self.SCALE_FACTOR)

        # One rect drives both the blit and the click test, so the whole icon is
        # clickable and it can't hang off the bottom edge. Deriving it from the
        # scaled surface keeps it correct if SCALE_FACTOR changes.
        self.sound_icon_rect = self.icon_sound_on.get_rect(
            bottomleft=(self.ICON_MARGIN, settings.HEIGHT - self.ICON_MARGIN)
        )

        self.logo_rect = self.logo.get_rect(midtop=(cx, 50))
        self.menu_rect = self.menu.get_rect(midtop=(cx, self.logo_rect.bottom + 50))

        button_offset_x = self.menu_rect.width // 2 - self.img_play_normal.get_width() // 2
        button_offset_y = 20 * SCALE_FACTOR  # padding
        self.btn_start_pos = (
            self.menu_rect.x + button_offset_x,
            self.menu_rect.y + button_offset_y,
        )
        self.btn_start = ImageButton(
            self.btn_start_pos, self.img_play_normal, self.img_play_hover, self.start_game
        )
        start_x, start_y = self.btn_start_pos
        quit_y = start_y + self.img_play_normal.get_height() + 20
        self.btn_quit = ImageButton(
            (start_x, quit_y), self.img_quit_normal, self.img_quit_hover, self.quit_game
        )
        self.buttons = [self.btn_start, self.btn_quit]

    def start_game(self) -> None:
        from turing_game.states.overworld import Overworld
        self.manager.change(Overworld(self.manager))

    def toggle_mute(self) -> None:
        self.game.sound_manager.toggle_mute()

    @staticmethod
    def quit_game() -> None:
        pygame.quit()
        sys.exit()

    def update(self, dt: float) -> None:
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mouse_pos)

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill((25, 32, 60))

        screen.blit(self.logo, self.logo_rect)

        screen.blit(self.menu, self.menu_rect)

        subtitle = self.game.font.render(
            'A game about the ethical use of Artificial Intelligence', True, settings.WHITE
        )
        subtitle_rect = subtitle.get_rect(
            center=(settings.WIDTH // 2, (self.logo_rect.bottom + self.menu_rect.top) // 2)
        )
        screen.blit(subtitle, subtitle_rect)

        for button in self.buttons:
            button.draw(screen)

        current_icon = self.icon_sound_off if self.game.sound_manager.muted else self.icon_sound_on
        screen.blit(current_icon, self.sound_icon_rect)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            for button in self.buttons:
                button.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.sound_icon_rect.collidepoint(event.pos):
                    self.toggle_mute()
