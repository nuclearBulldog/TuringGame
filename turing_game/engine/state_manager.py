from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pygame

    from turing_game.game import Game
    from turing_game.states.base_state import BaseState


class StateManager:
    """ holds only one active state at a time! """

    def __init__(self, game: Game) -> None:
        self.game = game
        self.state = None

    def change(self, new_state: BaseState) -> None:
        if self.state and hasattr(self.state, 'on_exit'):
            self.state.on_exit()

        self.state = new_state

        if self.state and hasattr(self.state, 'on_enter'):
            self.state.on_enter()

    def update(self, dt: float) -> None:
        self.state.update(dt)

    def draw(self, screen: pygame.Surface) -> None:
        self.state.draw(screen)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        self.state.handle_events(events)
