import pygame

class ImageButton:
    def __init__(self, pos, image_normal, image_hover, callback):
        self.image_normal = image_normal
        self.image_hover = image_hover
        self.image = self.image_normal
        self.rect = self.image.get_rect(topleft=pos)
        self.callback = callback
        self.is_hovered = False

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        self.image = self.image_hover if self.is_hovered else self.image_normal

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.callback()