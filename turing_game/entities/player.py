from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from turing_game.engine.camera import Camera

import pygame

from turing_game import settings
from turing_game.entities.base_entity import BaseEntity
from turing_game.systems import sprites
from turing_game.systems.animation import AnimationController


class Player(BaseEntity):
    """Platformer player with movement, gravity, collisions, and animations."""

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, 28, 40)
        self.on_ground = False
        self.facing_right = True
        self.animator = AnimationController(
            self._build_animations(),
            fps_by_state={'idle': 3, 'run': 10, 'jump': 1},
        )

    def _build_animations(self) -> dict[str, list[pygame.Surface]]:
        # Frames come from assets/player.png via the shared sheet loader; the
        # {idle,run,jump} keys stay identical so AnimationController is untouched.
        return sprites.load_player_states()

    def update(self, dt: float, solids: Iterable[pygame.sprite.Sprite]) -> None:
        keys = pygame.key.get_pressed()

        self.vel.x = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vel.x = -settings.PLAYER_SPEED
            self.facing_right = False
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vel.x = settings.PLAYER_SPEED
            self.facing_right = True

        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
            self.vel.y = settings.PLAYER_JUMP_VELOCITY
            self.on_ground = False

        self.vel.y += settings.GRAVITY * dt

        self.pos.x += self.vel.x * dt
        self.sync_rect()
        self._resolve_collisions(solids, horizontal=True)

        self.pos.y += self.vel.y * dt
        self.sync_rect()
        self.on_ground = False
        self._resolve_collisions(solids, horizontal=False)

        if not self.on_ground:
            self.animator.set_state('jump')
        elif abs(self.vel.x) > 0:
            self.animator.set_state('run')
        else:
            self.animator.set_state('idle')
        self.animator.update(dt)

    def _resolve_collisions(
        self, solids: Iterable[pygame.sprite.Sprite], horizontal: bool
    ) -> None:
        for tile in solids:
            if self.rect.colliderect(tile.rect):
                if horizontal:
                    if self.vel.x > 0:
                        self.rect.right = tile.rect.left
                    elif self.vel.x < 0:
                        self.rect.left = tile.rect.right
                    self.pos.x = self.rect.x
                else:
                    if self.vel.y > 0:
                        self.rect.bottom = tile.rect.top
                        self.on_ground = True
                    elif self.vel.y < 0:
                        self.rect.top = tile.rect.bottom
                    self.vel.y = 0
                    self.pos.y = self.rect.y

    def draw(self, screen: pygame.Surface, camera: Camera) -> None:
        image = self.animator.image()
        if not self.facing_right:
            image = pygame.transform.flip(image, True, False)
        draw_x = self.rect.x - 2
        draw_y = self.rect.y - 8
        screen.blit(image, (draw_x - camera.offset.x, draw_y - camera.offset.y))
