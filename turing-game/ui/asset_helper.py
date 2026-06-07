import pygame

sheet 

def cut_sprite(sheet, x, y, width, height):
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    sprite.blit(sheet, (0, 0 ), (x, y, width, height))
    return sprite

ui_elements = [

]