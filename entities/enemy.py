import pygame

# AI Generated BoilerPlate

import settings
from entities.base_entity import BaseEntity
from systems.animation import AnimationController

# Algorithim AI Generated

class Enemy(BaseEntity):
    """Enemy with a tiny AI state machine: patrol and chase."""

    def __init__(self, x, y, patrol_distance=120):
        super().__init__(x, y, 28, 36)
        self.patrol_min_x = x - patrol_distance
        self.patrol_max_x = x + patrol_distance

        self.direction = 1
        self.on_ground = False
        self.state = 'patrol'
        self.detection_radius = 200

        self.animator = AnimationController(
            self._build_animations(),
            fps_by_state={'idle': 2, 'run': 7},
        )

    def _build_animations(self):
        # AI Generated
        def make_frame(arm=0, leg=0):
            surf = pygame.Surface((32, 44), pygame.SRCALPHA)

            pygame.draw.circle(surf, (255, 240, 150), (16, 8), 6)
            pygame.draw.rect(surf, settings.RED, (9, 14, 14, 12), border_radius=4)

            pygame.draw.line(surf, settings.BLACK, (14, 26), (11 - leg, 40), 3)
            pygame.draw.line(surf, settings.BLACK, (18, 26), (21 + leg, 40), 3)
            pygame.draw.line(surf, settings.BLACK, (9, 18), (2, 18 + arm), 3)
            pygame.draw.line(surf, settings.BLACK, (23, 18), (30, 18 - arm), 3)

            return surf
        idle = [make_frame(0, 0), make_frame(1, 0)]
        run = [make_frame(0, 3), make_frame(0, -3), make_frame(1, 2), make_frame(-1, -2)]
        return {'idle': idle, 'run': run}

    def update(self, dt, player, solids):
        distance_x = player.rect.centerx - self.rect.centerx
        self.state = 'chase' if abs(distance_x) <= self.detection_radius else 'patrol'

        if self.state == 'patrol':
            self._patrol()
        else:
            self._chase(player)

        self.vel.y += settings.GRAVITY * dt
        self.pos.x += self.vel.x * dt
        self.sync_rect()
        self._resolve_collisions(solids, horizontal=True)
        self.pos.y += self.vel.y * dt
        self.sync_rect()
        self.on_ground = False
        self._resolve_collisions(solids, horizontal=False)

        self.animator.set_state('run' if abs(self.vel.x) > 1 else 'idle')
        self.animator.update(dt)

    def _patrol(self):
        # AI Generated
        self.vel.x = settings.ENEMY_SPEED * self.direction
        if self.rect.x <= self.patrol_min_x:
            self.direction = 1
        elif self.rect.x >= self.patrol_max_x:
            self.direction = -1

    def _chase(self, player):
        # AI Generated
        if player.rect.centerx < self.rect.centerx:
            self.direction = -1
            self.vel.x = -settings.ENEMY_SPEED
        else:
            self.direction = 1
            self.vel.x = settings.ENEMY_SPEED

    def _resolve_collisions(self, solids, horizontal):

        for tile in solids:
            if self.rect.colliderect(tile.rect):

                if horizontal:
                    if self.vel.x > 0:
                        self.rect.right = tile.rect.left
                        self.direction = -1
                    elif self.vel.x < 0:
                        self.rect.left = tile.rect.right
                        self.direction = 1
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

        if self.direction < 0:
            image = pygame.transform.flip(image, True, False)

        draw_x = self.rect.x - 2
        draw_y = self.rect.y - 8

        screen.blit(image, (draw_x - camera.offset.x, draw_y - camera.offset.y))
        color = settings.RED if self.state == 'patrol' else settings.YELLOW

        pygame.draw.circle(screen, color, (int(self.rect.centerx - camera.offset.x), int(self.rect.y - 12 - camera.offset.y)), 4)