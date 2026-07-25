import pygame
from systems import encounter_data, sprites


def test_resolve_prefers_explicit_sprite_key():
    assert sprites.resolve_enemy_sprite('study_bot', 'report_due') == 'study_bot'


def test_resolve_falls_back_to_encounter_id():
    assert sprites.resolve_enemy_sprite(None, 'exam_proctor') == 'exam_proctor'


def test_resolve_defaults_when_nothing_matches():
    assert sprites.resolve_enemy_sprite('nope', 'also_nope') == sprites.DEFAULT_ENEMY_SPRITE


def test_load_player_states_has_expected_shape():
    states = sprites.load_player_states()
    assert set(states) == {'idle', 'run', 'jump'}
    assert [len(states[s]) for s in ('idle', 'run', 'jump')] == [2, 4, 1]
    assert all(f.get_size() == sprites.PLAYER_FRAME for fs in states.values() for f in fs)


def test_load_enemy_states_has_expected_shape():
    states = sprites.load_enemy_states('deepfake_classmate')
    assert set(states) == {'idle', 'run'}
    assert [len(states['idle']), len(states['run'])] == [2, 4]
    assert all(f.get_size() == sprites.ENEMY_FRAME for fs in states.values() for f in fs)


def test_every_enemy_row_loads():
    for key in sprites.ENEMY_ROWS:
        frame = sprites.enemy_battle_frame(key)
        assert isinstance(frame, pygame.Surface)
        assert frame.get_size() == sprites.ENEMY_FRAME


def test_every_encounter_sprite_has_a_row():
    """Guards against a typo'd ``sprite`` silently defaulting to the wrong art.

    Reads the real encounter database on purpose: a mismatch here means a
    shipped encounter would render as ``report_due`` in battle instead of its
    own creature, which no other test would catch.
    """
    database = encounter_data.load_encounters()
    unknown = {
        eid: enc['sprite']
        for eid, enc in database.items()
        if 'sprite' in enc and enc['sprite'] not in sprites.ENEMY_ROWS
    }
    assert not unknown, f"encounters name sprites with no row in ENEMY_ROWS: {unknown}"
