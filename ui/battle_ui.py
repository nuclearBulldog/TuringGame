import pygame

import settings

class BattleUI:
    """Draws a Pokémon-style battle layout and move selector."""

    def __init__(self, font, big_font):
        self.font = font
        self.big_font = big_font

    def draw_hp_bar(self, screen, x, y, w, h, current, maximum):
        ratio = 0 if maximum <= 0 else current / maximum
        fill_w = int(w * ratio)

        pygame.draw.rect(screen, settings.WHITE, (x, y, w, h), border_radius=6)
        pygame.draw.rect(screen, settings.OUTLINE, (x, y, w, h), width=2, border_radius=6)

        color = settings.HP_GREEN if ratio > 0.35 else settings.HP_RED
        pygame.draw.rect(screen, color, (x + 2, y + 2, max(0, fill_w - 4), h - 4), border_radius=5)

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
        self._draw_background(screen) # draw background

        self.draw_creature(screen, 610, 42, settings.RED, facing_left=True) # draw enemy
        self.draw_creature(screen, 120, 205, settings.BLUE, facing_left=False) # draw player

        self._draw_enemy_panel(screen, battle_system) # enemys panel
        self._draw_player_panel(screen, battle_system) # players panel

        self._draw_bottom_ui(screen) # bottom ui
        self._draw_message_box(screen, battle_system.message) # message box

        self._draw_moves(screen, battle_system, selected_index) # draw potential moves

        hint = 'Arrows: Select   Enter: Use Move   Esc: Return to Menu' # hint
        screen.blit(self.font.render(hint, True, settings.BLACK), (20, 508)) # render hind

    # draw panel
    def _draw_panel(self, screen, rect):
        pygame.draw.rect(screen, settings.PANEL, rect, border_radius=12)
        pygame.draw.rect(screen, settings.OUTLINE, rect, width=3, border_radius=12)

    # draw enemy panel
    def _draw_enemy_panel(self, screen, battle):
        panel = pygame.Rect(520, 20, 300, 90)
        self._draw_panel(screen, panel)

        padding = 12

        # Name (top-left)
        name_pos = (panel.x + padding, panel.y + padding)
        screen.blit(self.big_font.render(battle.enemy_name, True, settings.BLACK), name_pos)

        # HP bar
        hp_x = panel.x + padding
        hp_y = panel.y + 40
        self.draw_hp_bar(screen, hp_x, hp_y, 170, 18, battle.enemy_hp, battle.enemy_max_hp)

        # HP text (right aligned)
        hp_text = f"{battle.enemy_hp}/{battle.enemy_max_hp}"
        text_surface = self.font.render(hp_text, True, settings.BLACK)
        text_rect = text_surface.get_rect(
            right=panel.right - padding,
            top=hp_y + 20
        )

        screen.blit(text_surface, text_rect)

    # draw player panel
    def _draw_player_panel(self, screen, battle):
        panel = pygame.Rect(400, 300, 330, 110)
        self._draw_panel(screen, panel)

        padding = 12

        # Name
        screen.blit(
            self.big_font.render(battle.player_name, True, settings.BLACK),
            (panel.x + padding, panel.y + padding)
        )

        # HP bar
        hp_y = panel.y + 50
        self.draw_hp_bar(
            screen,
            panel.x + padding,
            hp_y,
            210,
            20,
            battle.player_hp,
            battle.player_max_hp
        )

        # HP text (right aligned)
        hp_text = f"{battle.player_hp}/{battle.player_max_hp}"
        txt = self.font.render(hp_text, True, settings.BLACK)
        txt_rect = txt.get_rect(right=panel.right - padding, top=hp_y + 25)

        screen.blit(txt, txt_rect)

    # message box
    def _draw_message_box(self, screen, message):
        screen_w = screen.get_width()
        screen_h = screen.get_height()

        top = int(screen_h * 0.78)
        left_split = int(screen_w * 0.56)

        box = pygame.Rect(10, top + 10, left_split - 20, screen_h - top - 20)

        self._draw_panel(screen, box)

        padding = 15
        max_width = box.width - padding * 2

        lines = self._wrap_text(message, self.font, max_width)

        for i, line in enumerate(lines[:3]):
            text = self.font.render(line, True, settings.BLACK)
            screen.blit(text, (box.x + 15, box.y + 15 + i * 25))

    # background
    def _draw_background(self, screen):
        screen.fill((200, 235, 255))
        pygame.draw.rect(screen, (170, 220, 160), (0, 0, settings.WIDTH, settings.HEIGHT))

        pygame.draw.ellipse(screen, (150, 180, 120), (580, 110, 210, 50))
        pygame.draw.ellipse(screen, (150, 180, 120), (90, 285, 250, 70))

    # bottom ui
    def _draw_bottom_ui(self, screen):
        pygame.draw.rect(screen, settings.WHITE, (0, 420, settings.WIDTH, 120))
        pygame.draw.line(screen, settings.OUTLINE, (0, 420), (settings.WIDTH, 420), 3)
        pygame.draw.line(screen, settings.OUTLINE, (540, 420), (540, 540), 3)

    # draw potential moves
    def _draw_moves(self, screen, battle_system, selected_index):
        screen_w = screen.get_width()
        screen_h = screen.get_height()

        # --- Bottom UI area ---
        top = int(screen_h * 0.78)
        left_split = int(screen_w * 0.56)

        area_x = left_split
        area_y = top
        area_w = screen_w - left_split
        area_h = screen_h - top

        # --- Grid layout ---
        cols = 2
        rows = (len(battle_system.moves) + 1) // 2

        padding = int(screen_w * 0.01)

        button_w = (area_w - padding * (cols + 1)) // cols
        button_h = (area_h - padding * (rows + 1)) // rows

        for i, move in enumerate(battle_system.moves):
            row, col = divmod(i, cols)

            x = area_x + padding + col * (button_w + padding)
            y = area_y + padding + row * (button_h + padding)

            rect = pygame.Rect(x, y, button_w, button_h)

            selected = (
                    i == selected_index
                    and battle_system.turn == 'player'
                    and not battle_system.battle_over
            )

            fill = settings.YELLOW if selected else settings.PANEL

            pygame.draw.rect(screen, fill, rect, border_radius=10)
            pygame.draw.rect(screen, settings.OUTLINE, rect, 2, border_radius=10)

            text_surf = self.big_font.render(move.name, True, settings.BLACK)

            max_w = button_w - 10
            max_h = button_h - 10

            surf_w, surf_h = text_surf.get_size()
            if surf_w > max_w or surf_h > max_h:
                scale_factor = min(max_w / surf_w, max_h / surf_h)
                new_size = (int(surf_w * scale_factor), int(surf_h * scale_factor))

                text_surf = pygame.transform.smoothscale(text_surf, new_size)

            text_rect = text_surf.get_rect(center=(rect.center))
            screen.blit(text_surf, text_rect)

    # format text
    def _wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word

            # Measure rendered width
            text_width = font.size(test_line)[0]

            if text_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines
