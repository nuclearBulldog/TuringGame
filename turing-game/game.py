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

        # DEBUG
        pygame.font.init()
        from ui.debug_overlay import DebugOverlay
        self.debug_overlay = DebugOverlay(pygame.font.SysFont(None, 15)) if settings.DEBUG else None
        self.debug_elements = []


    def run(self):
        while self.running:

            # DEBUG
            debug_mouse_pos = pygame.mouse.get_pos() if settings.DEBUG else (0, 0)

            dt = self.clock.tick(settings.FPS) / 1000.0
            
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

                # DEBUG
                if settings.DEBUG and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F1:
                        self.debug_overlay.toggle()

                for element in self.debug_elements:
                    element.handle_event(event)

            self.state_manager.handle_events(events)
            self.state_manager.update(dt)
            self.state_manager.draw(self.screen)


            # DEBUG
            if settings.DEBUG:
                for element in self.debug_elements:
                    element.draw(self.screen)

                # Draw debug LAST (on top)
                if self.debug_overlay is not None:
                    self.debug_overlay.draw(self.screen, self.debug_elements, debug_mouse_pos, self.font)

            pygame.display.flip()
        pygame.quit()
