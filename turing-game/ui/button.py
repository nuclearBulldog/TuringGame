import pygame
import settings

# AI Generated BoilerPlate

class Button:
    """Simple reusable button with hover and click callback."""

    def __init__(self, rect, text, callback, font):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.font = font
        self.hovered = False

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()

    def draw(self, screen):
        fill = settings.YELLOW if self.hovered else settings.PANEL
        pygame.draw.rect(screen, fill, self.rect, border_radius=12)
        pygame.draw.rect(screen, settings.OUTLINE, self.rect, width=3, border_radius=12)
        text_surface = self.font.render(self.text, True, settings.BLACK)
        screen.blit(text_surface, text_surface.get_rect(center=self.rect.center))
