import pygame
import settings
from engine.state_manager import StateManager
from systems.sound_manager import SoundManager
from states.main_menu import MainMenu

class Game:
    def __init__(self):
        pygame.init()
        self.sound_manager = SoundManager()
        self.sound_manager.play_music(settings.BG_MUSIC)
        self.screen= pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        pygame.display.set_caption(settings.TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self._game_finished = False

        self.font = pygame.font.Font(settings.BASE_FONT, 20)
        self.big_font = pygame.font.Font(settings.BASE_FONT, 32)

        self.state_manager = StateManager(self)
        self.state_manager.change(MainMenu(self.state_manager))

    def run(self):
        while self.running:

            dt = self.clock.tick(settings.FPS) / 1000.0
            
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            self.state_manager.handle_events(events)
            self.state_manager.update(dt)
            self.state_manager.draw(self.screen)

            pygame.display.flip()
        pygame.quit()
