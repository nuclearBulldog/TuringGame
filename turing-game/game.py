import pygame
import settings
# import engine
# import states
# import ui
# import entities

# import engine.state_manager
# import engine.camera
# import states.battle
# import states.main_menu
# import states.overworld
# import states.pause_menu
# import ui.button
# import ui.hud
# import entities.player
# import entities.enemy


# from engine import *
# from states import *
# from ui import *
# from entities import *

from engine.state_manager import StateManager
from systems.sound_manager import SoundManager
from states.main_menu import MainMenu
#from states.overworld import Overworld
# from states.battle import BattleState
# # from states.pause_menu import PauseMenu
# from ui.button import Button
# # from ui.hud import Hud
# # from entities.enemy import Enemy
# from entities.player import Player


class Game:
    def __init__(self):
        pygame.init()
        self.sound = SoundManager()
        self.screen= pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        pygame.display.set_caption(settings.TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self._game_finished = False

        self.font = pygame.font.Font(settings.BASE_FONT, 16)
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



    # def handle_events(self):
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             self.running = False
    #     self.state_manager.handle_events()




# def check_collision(player, platforms):
#     player.on_ground = False
#
#     for p in platforms:
#         if player.rect.colliderect(p):
#             if player.vel.y > 0:  # falling
#                 player.rect.bottom = p.top
#                 player.vel.y = 0
#                 player.on_ground = True

    # while self.running:
    #     delta_time = FramePerSec.tick(FPS) / 1000
    #
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             running = False
    #
    #     state_manger.update(delta_time)
    #
    #     if player.rect.colliderect(enemy.rect):
    #         state_manger.change(BattleState(state_manger))
    #
    #     screen.fill((0,0,0))
    #     state_manger.draw(screen)
    #
    #     pygame.display.flip()
    #
    # pygame.quit()