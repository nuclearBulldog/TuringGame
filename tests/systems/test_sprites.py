import pygame
from systems import sprites


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
