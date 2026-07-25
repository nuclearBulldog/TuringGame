from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pygame

    from turing_game.engine.state_manager import StateManager


class BaseState:
    def __init__(self, manager: StateManager) -> None:
        self.manager = manager
        self.game = manager.game

    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, screen: pygame.Surface) -> None:
        pass

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        pass
