import pygame

import settings
from entities.base_entity import BaseEntity
from systems.animation import AnimationController

# AI Generated BoilerPlate

class Player(BaseEntity):
    """Platformer player with movement, gravity, collisions, and animations."""

    def __init__(self, x, y):
        super().__init__(x, y, 28, 40)
        self.on_ground = False
        self.facing_right = True
        self.animator = AnimationController(
            self._build_animations(),
            fps_by_state={'idle': 3, 'run': 10, 'jump': 1},
        )

    def _build_animations(self):
        # Placeholder sprites are drawn in code so the project works without asset files.
        def make_frame(body_offset=0, leg_offset=0, jump=False):
            surf = pygame.Surface((32, 48), pygame.SRCALPHA)
            pygame.draw.circle(surf, (245, 220, 180), (16, 8), 6)
            pygame.draw.rect(surf, settings.BLUE, (10, 14, 12, 14), border_radius=4)
            arm_y = 18 if not jump else 14
            pygame.draw.line(surf, settings.WHITE, (10, arm_y), (3, arm_y + body_offset), 3)
            pygame.draw.line(surf, settings.WHITE, (22, arm_y), (29, arm_y - body_offset), 3)
            leg_y = 28
            pygame.draw.line(surf, settings.BLACK, (14, leg_y), (12 - leg_offset, 42), 3)
            pygame.draw.line(surf, settings.BLACK, (18, leg_y), (20 + leg_offset, 42), 3)
            return surf
        idle = [make_frame(0, 0), make_frame(1, 0)]
        run = [make_frame(0, 3), make_frame(0, -3), make_frame(1, 2), make_frame(-1, -2)]
        jump = [make_frame(2, 1, jump=True)]
        return {'idle': idle, 'run': run, 'jump': jump}

    def update(self, dt, solids):
        keys = pygame.key.get_pressed()

        # Horizontal input.
        self.vel.x = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vel.x = -settings.PLAYER_SPEED
            self.facing_right = False
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vel.x = settings.PLAYER_SPEED
            self.facing_right = True

        # Jump only if grounded.
        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
            self.vel.y = settings.PLAYER_JUMP_VELOCITY
            self.on_ground = False

        # Gravity.
        self.vel.y += settings.GRAVITY * dt

        # Move horizontally and resolve collisions.
        self.pos.x += self.vel.x * dt
        self.sync_rect()
        self._resolve_collisions(solids, horizontal=True)

        # Move vertically and resolve collisions.
        self.pos.y += self.vel.y * dt
        self.sync_rect()
        self.on_ground = False
        self._resolve_collisions(solids, horizontal=False)

        # Select animation state.
        if not self.on_ground:
            self.animator.set_state('jump')
        elif abs(self.vel.x) > 0:
            self.animator.set_state('run')
        else:
            self.animator.set_state('idle')
        self.animator.update(dt)

    def _resolve_collisions(self, solids, horizontal):
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

    def draw(self, screen, camera):
        image = self.animator.image()
        if not self.facing_right:
            image = pygame.transform.flip(image, True, False)
        draw_x = self.rect.x - 2
        draw_y = self.rect.y - 8
        screen.blit(image, (draw_x - camera.offset.x, draw_y - camera.offset.y))




# import pygame
# from pygame import *
# import settings
# from entities.base_entity import BaseEntity

# vec = pygame.Vector2

# ACC = 0.5
# FRIC = -0.12

# class Player(BaseEntity):
#     def __init__(self, x, y):
#         super().__init__(x, y, 28, 40)
#         self.surf = pygame.Surface((30, 30))
#         self.surf.fill((128, 255, 40))
#         self.rect = self.surf.get_rect(center=(10, 420))

#         self.pos = vec((10, 385))
#         self.vel = vec(0,0)
#         self.acc = vec(0,0)

#         self.jumping = False

#     def move(self):
#         self.acc = vec(0, 0.5)

#         pressed_keys = pygame.key.get_pressed()

#         if pressed_keys[K_LEFT]:
#             self.acc.x = -ACC
#         if pressed_keys[K_RIGHT]:
#             self.acc.x = ACC
#         self.acc = ACC

#     def update(self):
#         hits = pygame.sprite.spritecollide(P1, platforms, False)
#         if self.vel.y > 0:
#             if hits:
#                 if self.pos.y < hits[0].rect.bottom:
#                     if hits[0].point:
#                         hits[0].point = False
#                         self.score += 1
#                     self.pos.y = hits[0].rect.top + 1
#                     self.vel.y = 0
#                     self.jumping = False

#     def jump(self):
#         hits = pygame.sprite.spritecollide(self, platforms, False)
#         if hits and not self.jumping:
#             self.jumping = True
#             self.vel.y = -15

#     def cancel_jump(self):
#         if self.jumping:
#             if self.vel.y < -3:
#                 self.vel.y = -3

