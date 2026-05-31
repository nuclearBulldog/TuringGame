import pygame
import settings
from states.base_state import BaseState
from systems.battle_system import BattleSystem


class Button:
    def __init__(self, rect, text, font, on_click):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.on_click = on_click

    def draw(self, screen, bg=(240, 240, 240), fg=(0, 0, 0), border=(0, 0, 0)):
        pygame.draw.rect(screen, bg, self.rect, border_radius=10)
        pygame.draw.rect(screen, border, self.rect, width=3, border_radius=10)

        surf = self.font.render(self.text, True, fg)
        screen.blit(surf, surf.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click()


class BattleResultState(BaseState):
    def __init__(self, manager, return_to_state=None, system = None):
        super().__init__(manager)
        self.return_to_state = return_to_state

        self.system = system if system else BattleSystem()


        self.win = (self.system.enemy_hp <= 0)

        # Optional details toggle
        self.show_details = False

        # Layout (tweak as needed)
        cx = settings.WIDTH // 2
        y0 = settings.HEIGHT // 2 - 40
        w, h = 240, 60
        gap = 20

        self.buttons = [
            Button((cx - w//2, y0, w, h), "Details", self.game.font, self.toggle_details),
            Button((cx - w//2, y0 + (h + gap), w, h), "Play Again", self.game.font, self.play_again),
            Button((cx - w//2, y0 + 2*(h + gap), w, h), "Main Menu", self.game.font, self.main_menu),
        ]

    def toggle_details(self):
        self.show_details = not self.show_details

    def play_again(self):
        from states.battle import BattleState
        from systems.battle_system import BattleSystem

        # Later: inject a generator or level ID here

        new_system = BattleSystem()# replacing this

        self.manager.change(
            BattleState(
                self.manager,
                return_to_state=self.return_to_state,
                system=new_system
            )
        )

    def main_menu(self):
        from states.main_menu import MainMenu
        self.manager.change(MainMenu(self.manager))

    def update(self, dt):
        pass

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.play_again()
                elif event.key == pygame.K_ESCAPE:
                    self.main_menu()

            for b in self.buttons:
                b.handle_event(event)

    def draw(self, screen):
        # Background color based on win/lose (matches prototype: green vs red)
        if self.win:
            screen.fill((30, 160, 60))   # green
        else:
            screen.fill((200, 40, 40))   # red

        title_font = self.game.big_font
        text_font = self.game.font

        title = "You Win Good Job!" if self.win else "You Have Lost... Get Good"
        title_surf = title_font.render(title, True, (255, 255, 255))
        screen.blit(title_surf, title_surf.get_rect(center=(settings.WIDTH//2, 120)))

        # Draw buttons
        for b in self.buttons:
            b.draw(screen)

        # Details panel (optional)
        if self.show_details:
            panel = pygame.Rect(80, 200, settings.WIDTH - 160, 220)
            pygame.draw.rect(screen, (255, 255, 255), panel, border_radius=12)
            pygame.draw.rect(screen, (0, 0, 0), panel, 3, border_radius=12)

            lines = self._build_detail_lines()
            y = panel.y + 20
            for line in lines:
                s = text_font.render(line, True, (0, 0, 0))
                screen.blit(s, (panel.x + 20, y))
                y += 28

    def _build_detail_lines(self):
        # Adapt to whatever your BattleSystem tracks
        # Examples based on your prototype "summary + points"
        lines = []
        lines.append("Summary:")
        # If you have a list like system.summary_items = [("foo", True), ("bar", False)]
        if hasattr(self.system, "summary_items"):
            for name, ok in self.system.summary_items:
                mark = "✓" if ok else "✗"
                lines.append(f"  {mark} {name}")

        if hasattr(self.system, "score"):
            lines.append(f"Points: {self.system.score}")

        # Add anything else you track (turns taken, damage, etc.)
        return lines
