import pygame

import settings

class BattleUI:
    """Draws a Pokémon-style battle layout and move selector."""

    def __init__(self, font, big_font):
        self.font = font
        self.big_font = big_font

    def draw_hp_bar(self, screen, x, y, w, h, current, maximum):
        ratio = 0 if maximum <= 0 else current / maximum

        fill_w = int((w - 4) * ratio)

        pygame.draw.rect(screen, settings.OUTLINE, (x, y, w, h))

        pygame.draw.rect(screen, (80, 85, 80), (x + 2, y + 2, w - 4, h - 4))

        if fill_w > 0:
            color = settings.HP_GREEN if ratio > 0.35 else settings.HP_RED
            pygame.draw.rect(screen, color, (x + 2, y + 2, fill_w, h - 4))

    def draw_creature(self, screen, x, y, color, facing_left=False):
        surf = pygame.Surface((96, 96), pygame.SRCALPHA)

        pygame.draw.ellipse(surf, color, (10, 25, 76, 46))
        pygame.draw.circle(surf, settings.WHITE, (34, 42), 8)
        pygame.draw.circle(surf, settings.BLACK, (35, 43), 3)
        pygame.draw.circle(surf, settings.WHITE, (62, 42), 8)
        pygame.draw.circle(surf, settings.BLACK, (61, 43), 3)

        pygame.draw.arc(surf, settings.BLACK, (30, 48, 36, 20), 3.4, 6.0, 3)

        if facing_left:
            surf = pygame.transform.flip(surf, True, False)
        screen.blit(surf, (x, y))

    def draw(self, screen, battle_system, selected_index):
        self._draw_background(screen)

        self.draw_creature(screen, 610, 42, settings.RED, facing_left=True)
        self.draw_creature(screen, 120, 205, settings.BLUE, facing_left=False)

        self._draw_enemy_panel(screen, battle_system)
        self._draw_player_panel(screen, battle_system)

        self._draw_bottom_ui(screen)
        is_player_turn = (battle_system.turn == 'player' and not battle_system.battle_over)
        self._draw_message_box(screen, battle_system.message, show_hint=is_player_turn)

        self._draw_moves(screen, battle_system, selected_index)

    def _draw_panel(self, screen, rect):
        """Draws a classic RPG double-frame window overlay."""
        pygame.draw.rect(screen, settings.OUTLINE, rect)

        inner_rect = rect.inflate(-6, -6)
        pygame.draw.rect(screen, settings.PANEL, inner_rect)

        pygame.draw.rect(screen, settings.WHITE, inner_rect, width=2)

    def _draw_enemy_panel(self, screen, battle):
        panel = pygame.Rect(520, 20, 300, 90)
        self._draw_panel(screen, panel)

        padding = 14

        screen.blit(self.big_font.render(battle.enemy_name, False, settings.BLACK),
                    (panel.x + padding, panel.y + padding))

        hp_x = panel.x + padding
        hp_y = panel.y + 42
        self.draw_hp_bar(screen, hp_x, hp_y, 170, 16, battle.enemy_hp, battle.enemy_max_hp)

        hp_text = f"{battle.enemy_hp}/{battle.enemy_max_hp}"
        text_surface = self.big_font.render(hp_text, False, settings.BLACK)
        text_rect = text_surface.get_rect(right=panel.right - padding, top=hp_y + 20)
        screen.blit(text_surface, text_rect)

    def _draw_player_panel(self, screen, battle):
        panel = pygame.Rect(400, 290, 330, 110)
        self._draw_panel(screen, panel)

        padding = 14

        screen.blit(self.big_font.render(battle.player_name, False, settings.BLACK),
                    (panel.x + padding, panel.y + padding))

        hp_y = panel.y + 52
        self.draw_hp_bar(screen, panel.x + padding, hp_y, 210, 18, battle.player_hp, battle.player_max_hp)

        hp_text = f"{battle.player_hp}/{battle.player_max_hp}"
        txt = self.font.render(hp_text, False, settings.BLACK)
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
        lines = self._wrap_text(message, self.font, max_width)

        for i, line in enumerate(lines[:2]):
            text = self.font.render(line, False, settings.BLACK)
            # Increased line spacing slightly to 26 for better readability
            screen.blit(text, (box.x + 15, box.y + 15 + i * 26))

        if show_hint:
            hint = 'Arrows: Select   Enter: Use   Esc: Menu'
            # Drawing it in dark gray (100,100,100) so it doesn't clash with the main black text
            hint_surf = self.font.render(hint, False, (100, 100, 100))
            screen.blit(hint_surf, (box.x + 15, box.bottom - 24))

    def _draw_background(self, screen):
        screen.fill((180, 215, 235))
        pygame.draw.rect(screen, (155, 200, 145), (0, 0, settings.WIDTH, settings.HEIGHT))

        pygame.draw.ellipse(screen, (135, 165, 110), (580, 115, 210, 45))
        pygame.draw.ellipse(screen, (135, 165, 110), (90, 290, 250, 65))

    def _draw_bottom_ui(self, screen):
        pygame.draw.rect(screen, settings.PANEL, (0, 420, settings.WIDTH, 120))
        pygame.draw.line(screen, settings.OUTLINE, (0, 420), (settings.WIDTH, 420), 4)
        pygame.draw.line(screen, settings.OUTLINE, (520, 420), (520, 540), 4)

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

        for i, move in enumerate(battle_system.moves[:4]):  # Cap layout configuration to 4 standard moves
            row, col = divmod(i, cols)

            x = area_x + padding + col * (button_w + padding)
            y = area_y + padding + row * (button_h + padding)

            rect = pygame.Rect(x, y, button_w, button_h)

            selected = (
                    i == selected_index
                    and battle_system.turn == 'player'
                    and not battle_system.battle_over
            )

            # Draw the retro box outline
            pygame.draw.rect(screen, settings.OUTLINE, rect)
            inner = rect.inflate(-4, -4)

            fill = settings.YELLOW if selected else settings.PANEL
            pygame.draw.rect(screen, fill, inner)

            chosen_font = self.big_font
            text_width = chosen_font.size(move.name)[0]
            if text_width > (button_w - 12):
                chosen_font = self.font  # Falls back automatically to smaller legible text

            text_surf = chosen_font.render(move.name, False, settings.BLACK)
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)

    def _wrap_text(self, text, font, max_width):
        # Split by explicit newlines first
        raw_lines = text.split('\n')
        wrapped_lines = []

        for raw_line in raw_lines:
            words = raw_line.split(' ')  # Split by spaces
            current_line = ""

            for word in words:
                if not word: continue
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