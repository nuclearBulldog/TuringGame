import pygame
import settings
from engine.camera import Camera
from states.base_state import BaseState
from world.level import Level


class Overworld(BaseState):
    """A view/controller over a persistent :class:`~world.level.Level`.

    The level (tile map, player, enemies, cleared-encounter set, score) outlives
    this state: on a win the battle result resumes THIS same instance, so
    defeated enemies stay gone and progress is preserved.
    """

    # Seconds after (re)entering the overworld before enemy collisions can start
    # a battle. Stops a resumed battle from re-triggering on the frame the player
    # reappears standing on the spot where the last enemy died.
    RECOLLISION_GRACE = 0.4

    def __init__(self, manager, level=None):
        super().__init__(manager)
        self.level = level if level is not None else Level.load_random()
        self.camera = Camera()
        self._battle_started = False
        self._grace_timer = self.RECOLLISION_GRACE
        self._pending_enemy = None

    @property
    def player(self):
        return self.level.player

    @property
    def enemies(self):
        return self.level.enemies

    @property
    def tilemap(self):
        return self.level.tilemap

    def on_enter(self):
        # Called each time the state becomes active, including on resume after a
        # battle. Re-arm the grace window and clear the per-visit battle flag.
        self._battle_started = False
        self._grace_timer = self.RECOLLISION_GRACE

    def update(self, dt):
        self._battle_started = False
        if self._grace_timer > 0:
            self._grace_timer -= dt

        self.player.update(dt, self.tilemap.tiles)

        for enemy in self.enemies:
            enemy.update(dt, self.player, self.tilemap.tiles)

            if (self._grace_timer <= 0
                    and self.player.rect.colliderect(enemy.rect)
                    and not self._battle_started):
                self._battle_started = True
                self._start_battle(enemy)
                return

        goal = self.tilemap.goal_rect
        if goal is not None and self.player.rect.colliderect(goal):
            from states.level_complete import LevelCompleteState
            self.manager.change(LevelCompleteState(self.manager, level=self.level))
            return

        self.camera.update(self.player.rect)

    def _start_battle(self, enemy):
        self._pending_enemy = enemy

        from states.battle import BattleState
        from systems.battle_system import BattleSystem
        system = BattleSystem(encounter_id=enemy.encounter_id)
        self.manager.change(BattleState(self.manager, return_to_state=self, system=system))

    def resolve_won_battle(self, system):
        """Called by the battle result when the player wins: retire the enemy."""
        if self._pending_enemy is not None:
            self.level.clear_encounter(self._pending_enemy, system.score)
            self._pending_enemy = None

    def draw(self, screen):
        screen.fill(settings.SKY)
        pygame.draw.circle(screen, (255, 245, 150), (820, 90), 35)
        pygame.draw.rect(screen, (160, 210, 255), (0, 390, settings.WIDTH, settings.HEIGHT - 390))
        self.tilemap.draw(screen, self.camera)

        self._draw_goal(screen)

        for enemy in self.enemies:
            enemy.draw(screen, self.camera)

        self.player.draw(screen, self.camera)
        self._draw_hud(screen)

    def _draw_goal(self, screen):
        goal = self.tilemap.goal_rect
        if goal is None:
            return
        rect = self.camera.apply_rect(goal)
        # A simple flag: pole plus a red pennant.
        pole_x = rect.x + 3
        pygame.draw.rect(screen, settings.OUTLINE, (pole_x, rect.y - 28, 3, rect.height + 28))
        pygame.draw.polygon(
            screen, settings.RED,
            [(pole_x + 3, rect.y - 28), (pole_x + 22, rect.y - 21), (pole_x + 3, rect.y - 14)],
        )

    def _draw_hud(self, screen):
        panel = pygame.Rect(12, 12, 360, 76)
        pygame.draw.rect(screen, settings.WHITE, panel, border_radius=12)
        pygame.draw.rect(screen, settings.OUTLINE, panel, width=3, border_radius=12)
        cleared = len(self.level.cleared_encounters)
        total = cleared + len(self.enemies)
        lines = [
            f'Encounters cleared: {cleared}/{total}',
            'Move: A/D or Arrow Key Left/Arrow Key Right',
            'Jump: Space | W | Arrow Key Up   ·   Reach the flag!',
        ]

        for i, text in enumerate(lines):
            font = self.game.big_font if i == 0 else self.game.font
            img = font.render(text, True, settings.BLACK)
            screen.blit(img, (24, 18 + i * 22))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                self.game.sound_manager.toggle_mute()
