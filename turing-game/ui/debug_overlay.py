import pygame
import settings

pygame.init()

def draw_rect_outline(screen, rect, colour=(0, 255, 0), width=1):
    pygame.draw.rect(screen, colour, rect, width)

class DebugOverlay:
    def __init__(self, font):
        self.font = font
        self.enabled = False

    def toggle(self):
        self.enabled = not self.enabled

    def draw(self, surf, elements, mouse_pos, font):
        if not settings.DEBUG or not self.enabled:
            return

        x, y = mouse_pos
        text = font.render(f'Mouse Position: (X: {x}, Y: {y})', True, (255, 255, 0))
        surf.blit(text, (x, y))

        hovered = None
        for element in elements:
            if element.collidepoint(mouse_pos):
                hovered = element

        for element in elements:
            colour = (0, 255, 0) if element is not hovered else (255, 0, 255)
            draw_rect_outline(surf, element.rect, colour=colour, width=2 if element is not hovered else 1)

            label = font.render(element.name, True, colour)
            surf.blit(label, (element.rect.x, element.rect.y - 14))
