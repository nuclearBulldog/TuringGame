from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pygame


class AnimationController:
    """Stores named animations and advances frames for the active state."""

    def __init__(
        self,
        animations: dict[str, list[pygame.Surface]],
        fps_by_state: dict[str, float] | None = None,
    ) -> None:
        self.animations = animations
        self.fps_by_state = fps_by_state or {name: 6 for name in animations}
        self.current = next(iter(animations))
        self.frame_index = 0.0

    def set_state(self, state_name: str) -> None:
        if state_name != self.current:
            self.current = state_name
            self.frame_index = 0.0

    def update(self, dt: float) -> None:
        frames = self.animations[self.current]
        if len(frames) <= 1:
            return
        fps = self.fps_by_state.get(self.current, 6)
        self.frame_index = (self.frame_index + fps * dt) % len(frames)

    def image(self) -> pygame.Surface:
        return self.animations[self.current][int(self.frame_index)]
