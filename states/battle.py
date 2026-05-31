import pygame

from states.base_state import BaseState
from systems.battle_system import BattleSystem
from ui.battle_ui import BattleUI

class BattleState(BaseState):
    def __init__(self, manager, return_to_state=None):
        super().__init__(manager)
        self.return_to_state = return_to_state
        self.system = BattleSystem()
        self.ui = BattleUI(self.game.font, self.game.big_font) 
        self.selected_move = 0 
        self.enemy_action_delay = 0.55 
        self.enemy_timer = 0.0
        self.finished_timer = 0.0
        self.finished_delay = 0.5
        self._result_shown = False

    def update(self, dt):
       if self.system.turn == 'enemy' and not self.system.battle_over:
            self.enemy_timer += dt
            if self.enemy_timer >= self.enemy_action_delay:
                self.enemy_timer = 0.0
                self.system.enemy_take_turn()

       if self.system.battle_over and not self._result_shown:
           self.finished_timer += dt
           if self.finished_timer >= self.finished_delay:
               self._result_shown = True
               from states.battle_result import BattleResultState
               self.manager.change(
                   BattleResultState(
                       self.manager,
                       system=self.system,
                       return_to_state=self.return_to_state
                   )
               )

    def draw(self, screen):
        self.ui.draw(screen, self.system, self.selected_move)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from states.main_menu import MainMenu

                    self.manager.change(MainMenu(self.manager))
                    return

                if self.system.turn != 'player' or self.system.battle_over:
                    continue

                if event.key == pygame.K_LEFT:
                    if self.selected_move % 2 == 1:
                        self.selected_move -= 1

                elif event.key == pygame.K_RIGHT:
                    if self.selected_move % 2 == 0 and self.selected_move + 1 < len(self.system.moves):
                        self.selected_move += 1

                elif event.key == pygame.K_UP:
                    if self.selected_move - 2 >= 0:
                        self.selected_move -= 2

                elif event.key == pygame.K_DOWN:
                    if self.selected_move + 2 < len(self.system.moves):
                        self.selected_move += 2

                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.system.player_use_move(self.selected_move)

