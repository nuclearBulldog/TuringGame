import pygame
from systems.battle_system import BattleSystem
from ui.battle_ui import BattleUI


def _ui():
    return BattleUI(pygame.font.Font(None, 20), pygame.font.Font(None, 32))


def test_battle_system_exposes_default_sprite_key():
    # Real encounter data now carries a sprite; the field is always present.
    assert BattleSystem(encounter_id='report_due').sprite_key == 'report_due'


def test_battle_ui_draw_runs_headless():
    ui = _ui()
    system = BattleSystem(encounter_id='report_due')
    screen = pygame.Surface((960, 580))
    ui.draw(screen, system, selected_index=0)  # should not raise


def test_battle_ui_draw_covers_selected_and_over_states():
    ui = _ui()
    system = BattleSystem(encounter_id='deepfake_classmate')
    screen = pygame.Surface((960, 580))
    ui.draw(screen, system, selected_index=2)   # a selected move highlighted
    system.enemy_hp = 0                          # battle_over branch, no hint/selection
    ui.draw(screen, system, selected_index=1)


def test_update_triggers_flash_on_enemy_hp_drop():
    ui = _ui()
    system = BattleSystem(encounter_id='report_due')
    ui.update(0.016, system)                     # seed last-seen HP
    assert ui._enemy_flash == 0.0
    system.enemy_hp -= 20                         # take damage
    ui.update(0.016, system)
    assert ui._enemy_flash > 0.0
    assert ui._enemy_shake > 0.0


def test_update_is_safe_without_hp_attributes():
    ui = _ui()

    class Bare:
        pass

    ui.update(0.016, Bare())                      # no enemy_hp/player_hp -> no crash
    assert ui._enemy_flash == 0.0
