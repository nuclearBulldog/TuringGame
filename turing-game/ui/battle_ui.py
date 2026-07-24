import pygame
import settings
from systems import sprites, spritesheet


class BattleUI:
    """Draws a Pokemon-style battle layout and move selector.

    Owns the transient *presentation* state (hit-flash + shake timers) so the
    battle rules in ``systems/battle_system.py`` stay drawing-free. HP is read
    defensively via ``getattr`` so lightweight mock systems still work.
    """

    # Where each combatant stands, aligned to the pads baked into battle_bg.png.
    ENEMY_POS = (648, 120)
    ENEMY_SIZE = (64, 88)
    PLAYER_POS = (150, 243)
    PLAYER_SIZE = (64, 96)

    # Damage-feedback feel — tune these to taste.
    FLASH_TIME = 0.18
    SHAKE_TIME = 0.30
    SHAKE_MAG = 7

    def __init__(self, font, big_font):
        self.font = font
        self.big_font = big_font

        self.bg = spritesheet.load_sheet(sprites.BATTLE_BG)
        self.hp_frame = spritesheet.load_sheet(sprites.HP_FRAME)

        self._player_img = None
        self._enemy_img = None
        self._enemy_key = None

        self._last_enemy_hp = None
        self._last_player_hp = None
        self._enemy_flash = 0.0
        self._player_flash = 0.0
        self._enemy_shake = 0.0
        self._player_shake = 0.0

    # -- feedback -----------------------------------------------------------
    def update(self, dt, battle_system):
        """Advance flash/shake timers; a drop in either HP starts a new pulse."""
        enemy_hp = getattr(battle_system, 'enemy_hp', None)
        player_hp = getattr(battle_system, 'player_hp', None)

        if (enemy_hp is not None and self._last_enemy_hp is not None
                and enemy_hp < self._last_enemy_hp):
            self._enemy_flash = self.FLASH_TIME
            self._enemy_shake = self.SHAKE_TIME
        if (player_hp is not None and self._last_player_hp is not None
                and player_hp < self._last_player_hp):
            self._player_flash = self.FLASH_TIME
            self._player_shake = self.SHAKE_TIME

        self._last_enemy_hp = enemy_hp
        self._last_player_hp = player_hp

        self._enemy_flash = max(0.0, self._enemy_flash - dt)
        self._player_flash = max(0.0, self._player_flash - dt)
        self._enemy_shake = max(0.0, self._enemy_shake - dt)
        self._player_shake = max(0.0, self._player_shake - dt)

    def _shake_offset(self, remaining):
        if remaining <= 0:
            return 0
        magnitude = self.SHAKE_MAG * (remaining / self.SHAKE_TIME)
        step = int(remaining * 60)
        return int(magnitude) * (1 if step % 2 else -1)

    def _flash_overlay(self, image, remaining):
        mask = pygame.mask.from_surface(image)
        overlay = mask.to_surface(setcolor=settings.HIT_FLASH, unsetcolor=(0, 0, 0, 0))
        overlay.set_alpha(int(255 * remaining / self.FLASH_TIME))
        return overlay

    # -- sprites ------------------------------------------------------------
    def _ensure_creatures(self, battle_system):
        key = getattr(battle_system, 'sprite_key', sprites.DEFAULT_ENEMY_SPRITE)
        if self._player_img is None:
            self._player_img = pygame.transform.scale(
                sprites.player_battle_frame(), self.PLAYER_SIZE)
        if key != self._enemy_key:
            self._enemy_key = key
            self._enemy_img = pygame.transform.scale(
                sprites.enemy_battle_frame(key), self.ENEMY_SIZE)

    def _draw_creature(self, screen, image, pos, flash, shake):
        dx = self._shake_offset(shake)
        where = (pos[0] + dx, pos[1])
        screen.blit(image, where)
        if flash > 0:
            screen.blit(self._flash_overlay(image, flash), where)

    # -- top-level draw -----------------------------------------------------
    def draw(self, screen, battle_system, selected_index):
        self._ensure_creatures(battle_system)
        self._draw_background(screen)

        self._draw_creature(screen, self._enemy_img, self.ENEMY_POS,
                            self._enemy_flash, self._enemy_shake)
        self._draw_creature(screen, self._player_img, self.PLAYER_POS,
                            self._player_flash, self._player_shake)

        self._draw_enemy_panel(screen, battle_system)
        self._draw_player_panel(screen, battle_system)

        self._draw_bottom_ui(screen)
        is_player_turn = (battle_system.turn == 'player' and not battle_system.battle_over)
        self._draw_message_box(screen, battle_system.message, show_hint=is_player_turn)

        self._draw_moves(screen, battle_system, selected_index)

    def _draw_background(self, screen):
        screen.blit(self.bg, (0, 0))

    # -- HP bar -------------------------------------------------------------
    def draw_hp_bar(self, screen, x, y, w, h, current, maximum):
        ratio = 0 if maximum <= 0 else current / maximum
        frame = pygame.transform.scale(self.hp_frame, (w, h))
        screen.blit(frame, (x, y))

        inset = 3
        track_w = w - inset * 2
        fill_w = int(track_w * ratio)
        if fill_w > 0:
            colour = settings.HP_FILL_HIGH if ratio > 0.35 else settings.HP_FILL_LOW
            pygame.draw.rect(screen, colour, (x + inset, y + inset, fill_w, h - inset * 2))

    # -- windows ------------------------------------------------------------
    def _draw_panel(self, screen, rect):
        """Draws a classic RPG double-frame window overlay."""
        pygame.draw.rect(screen, settings.UI_FRAME, rect)
        inner_rect = rect.inflate(-6, -6)
        pygame.draw.rect(screen, settings.UI_PANEL, inner_rect)
        pygame.draw.rect(screen, settings.UI_PANEL_EDGE, inner_rect, width=2)

    def _draw_enemy_panel(self, screen, battle):
        panel = pygame.Rect(520, 20, 300, 90)
        self._draw_panel(screen, panel)

        padding = 14
        screen.blit(self.big_font.render(battle.enemy_name, False, settings.UI_TEXT),
                    (panel.x + padding, panel.y + padding))

        hp_x = panel.x + padding
        hp_y = panel.y + 42
        self.draw_hp_bar(screen, hp_x, hp_y, 170, 16, battle.enemy_hp, battle.enemy_max_hp)

        hp_text = f"{battle.enemy_hp}/{battle.enemy_max_hp}"
        text_surface = self.big_font.render(hp_text, False, settings.UI_TEXT)
        text_rect = text_surface.get_rect(right=panel.right - padding, top=hp_y + 20)
        screen.blit(text_surface, text_rect)

    def _draw_player_panel(self, screen, battle):
        panel = pygame.Rect(400, 290, 330, 110)
        self._draw_panel(screen, panel)

        padding = 14
        screen.blit(self.big_font.render(battle.player_name, False, settings.UI_TEXT),
                    (panel.x + padding, panel.y + padding))

        hp_y = panel.y + 52
        self.draw_hp_bar(
            screen, panel.x + padding, hp_y, 210, 18, battle.player_hp, battle.player_max_hp
        )

        hp_text = f"{battle.player_hp}/{battle.player_max_hp}"
        txt = self.font.render(hp_text, False, settings.UI_TEXT)
        txt_rect = txt.get_rect(right=panel.right - padding, top=hp_y + 24)
        screen.blit(txt, txt_rect)

    def _draw_message_box(self, screen, message, show_hint=True):
        screen_w = screen.get_width()
        screen_h = screen.get_height()

        top = int(screen_h * 0.78)
        left_split = int(screen_w * 0.54)

        box = pygame.Rect(10, top + 10, left_split - 20, screen_h - top - 20)
        self._draw_panel(screen, box)

        padding = 15
        max_width = box.width - padding * 2
        lines = self._wrap_text(message, self.big_font, max_width)

        for i, line in enumerate(lines[:2]):
            text = self.big_font.render(line, False, settings.UI_TEXT)
            screen.blit(text, (box.x + 15, box.y + 15 + i * 26))

        if show_hint:
            hint = 'Arrows: Select   Enter: Use   Esc: Menu'
            hint_surf = self.font.render(hint, False, settings.UI_HINT)
            screen.blit(hint_surf, (box.x + 15, box.bottom - 24))

    def _draw_bottom_ui(self, screen):
        pygame.draw.rect(screen, settings.UI_PANEL, (0, 420, settings.WIDTH, 120))
        pygame.draw.line(screen, settings.UI_FRAME, (0, 420), (settings.WIDTH, 420), 4)
        pygame.draw.line(screen, settings.UI_FRAME, (520, 420), (520, 540), 4)

    def _draw_moves(self, screen, battle_system, selected_index):
        screen_w = screen.get_width()
        screen_h = screen.get_height()

        top = int(screen_h * 0.78)
        left_split = int(screen_w * 0.54)

        area_x = left_split
        area_y = top
        area_w = screen_w - left_split
        area_h = screen_h - top

        cols = 2
        padding = 8

        button_w = (area_w - padding * (cols + 1)) // cols
        button_h = (area_h - padding * 3) // 2

        for i, move in enumerate(battle_system.moves[:4]):
            row, col = divmod(i, cols)

            x = area_x + padding + col * (button_w + padding)
            y = area_y + padding + row * (button_h + padding)
            rect = pygame.Rect(x, y, button_w, button_h)

            selected = (
                i == selected_index
                and battle_system.turn == 'player'
                and not battle_system.battle_over
            )

            inner = rect.inflate(-4, -4)
            if selected:
                pygame.draw.rect(screen, settings.MOVE_SELECT_EDGE, rect)
                pygame.draw.rect(screen, settings.MOVE_SELECT_FILL, inner)
                pygame.draw.rect(screen, settings.MOVE_SELECT_EDGE, inner, width=3)
                # a small pointer so the choice is unmistakable
                pygame.draw.polygon(screen, settings.UI_FRAME, [
                    (rect.x + 6, rect.centery - 5),
                    (rect.x + 6, rect.centery + 5),
                    (rect.x + 13, rect.centery),
                ])
            else:
                pygame.draw.rect(screen, settings.UI_FRAME, rect)
                pygame.draw.rect(screen, settings.MOVE_IDLE_FILL, inner)

            chosen_font = self.big_font
            text_width = chosen_font.size(move.name)[0]
            if text_width > (button_w - 12):
                chosen_font = self.font

            text_surf = chosen_font.render(move.name, False, settings.UI_TEXT)
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)

    def _wrap_text(self, text, font, max_width):
        raw_lines = text.split('\n')
        wrapped_lines = []

        for raw_line in raw_lines:
            words = raw_line.split(' ')
            current_line = ""

            for word in words:
                if not word:
                    continue
                test_line = current_line + (" " if current_line else "") + word
                text_width = font.size(test_line)[0]

                if text_width <= max_width:
                    current_line = test_line
                else:
                    wrapped_lines.append(current_line)
                    current_line = word

            if current_line:
                wrapped_lines.append(current_line)

        return wrapped_lines
