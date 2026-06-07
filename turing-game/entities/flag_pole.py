# AI Generated BoilerPlate

import pygame


class FlagPole(BaseEntity):
    """Enemy with a tiny AI state machine: patrol and chase."""

    def __init__(self, x, y, patrol_distance=120):
        super().__init__(x, y, 28, 36)
        self.direction = 1
        self.on_ground = False

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
