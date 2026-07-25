from __future__ import annotations

from collections.abc import Callable

import pygame


class ImageButton:
    def __init__(
        self,
        pos: tuple[int, int],
        image_normal: pygame.Surface,
        image_hover: pygame.Surface,
        callback: Callable[[], None],
    ) -> None:
        self.image_normal = image_normal
        self.image_hover = image_hover
        self.image = self.image_normal
        self.rect = self.image.get_rect(topleft=pos)
        self.callback = callback
        self.is_hovered = False

    def update(self, mouse_pos: tuple[int, int]) -> None:
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        self.image = self.image_hover if self.is_hovered else self.image_normal

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.callback()
