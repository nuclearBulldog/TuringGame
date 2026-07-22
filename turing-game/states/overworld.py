import pygame

import settings
from engine.camera import Camera
from entities.enemy import Enemy
from entities.player import Player
from states.base_state import BaseState
from world.tilemap import TileMap


class Overworld(BaseState):

    def __init__(self, manager):
        super().__init__(manager)
        level_rows = settings.LEVEL_DIR / 'level1.csv'
        self.tilemap = TileMap(level_rows)
        px, py = self.tilemap.player_spawn
        self.player = Player(px, py)
        self.camera = Camera()
        self.enemies = [Enemy(x, y) for (x, y) in self.tilemap.enemy_spawns] or [Enemy(620, 180)]
        self._battle_started = False
        self._game_finished = False

    def update(self, dt):
        self._battle_started = False
        self.player.update(dt, self.tilemap.tiles)

        for enemy in self.enemies:
            enemy.update(dt, self.player, self.tilemap.tiles)

            if self.player.rect.colliderect(enemy.rect) and not self._battle_started:
                self._battle_started = True

                return_state = Overworld(self.manager)
                return_state.player.pos.xy = self.player.pos.xy
                return_state.player.sync_rect()

                remaining_positions = [e.pos.xy for e in self.enemies if e is not enemy]
                return_state.enemies = [Enemy(x, y) for (x, y) in remaining_positions]

                from states.battle import BattleState
                self.manager.change(BattleState(self.manager, return_to_state=return_state))
                return

        self.camera.update(self.player.rect)

    def draw(self, screen):
        screen.fill(settings.SKY)
        pygame.draw.circle(screen, (255, 245, 150), (820, 90), 35)
        pygame.draw.rect(screen, (160, 210, 255), (0, 390, settings.WIDTH, settings.HEIGHT - 390))
        self.tilemap.draw(screen, self.camera)

        for enemy in self.enemies:
            enemy.draw(screen, self.camera)

        self.player.draw(screen, self.camera)
        self._draw_hud(screen)

    def _draw_hud(self, screen):
        panel = pygame.Rect(12, 12, 360, 76)
        pygame.draw.rect(screen, settings.WHITE, panel, border_radius=12)
        pygame.draw.rect(screen, settings.OUTLINE, panel, width=3, border_radius=12)
        lines = [
            'Overworld',
            'Move: A/D or Arrow Key Left/Arrow Key Right',
            'Jump: Space | W | Arrow Key Up'
        ]

        for i, text in enumerate(lines):
            font = self.game.big_font if i == 0 else self.game.font
            img = font.render(text, True, settings.BLACK)
            screen.blit(img, (24, 18 + i * 22))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                self.game.sound_manager.toggle_mute()
