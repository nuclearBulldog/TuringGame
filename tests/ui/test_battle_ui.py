import pygame
import pytest

from turing_game import settings
from turing_game.systems import encounter_data
from turing_game.systems.battle_system import BattleSystem
from turing_game.ui.battle_ui import BattleUI


def _ui():
    return BattleUI(pygame.font.Font(None, 20), pygame.font.Font(None, 32))


def _every_battle_message():
    """Every string the message box can be asked to render, from real game data."""
    for encounter in encounter_data.load_encounters().values():
        yield encounter['intro_message']
        for move in encounter['moves']:
            if move.get('outcome'):
                yield move['outcome']['message']
            else:
                yield (f"You decided to {move['name']}, {move['description']}... "
                       f"dealing {abs(move['damage'])} damage!")


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


@pytest.mark.parametrize('show_hint', [True, False])
def test_no_battle_message_is_truncated(real_font, show_hint):
    """Every line of every message must survive the fit, in both hint states.

    Regression guard: the box used to hard-slice to two big_font rows, which cut
    the tail off 20 of the 25 messages - and the tail is where each scenario's
    consequence lands. Needs real font metrics, hence ``real_font``.
    """
    ui = BattleUI(real_font(settings.BASE_FONT, 20), real_font(settings.BASE_FONT, 32))
    screen = pygame.Surface((settings.WIDTH, settings.HEIGHT))
    box = ui.message_box_rect(screen)
    max_width, _, max_height = ui.message_text_budget(box, show_hint)

    for message in _every_battle_message():
        font, lines = ui._fit_message(message, max_width, max_height)
        assert ' '.join(lines).split() == message.split(), f'truncated: {message!r}'
        assert len(lines) * font.get_linesize() <= max_height, f'overflows box: {message!r}'
        for line in lines:
            assert font.size(line)[0] <= max_width, f'overflows width: {line!r}'
