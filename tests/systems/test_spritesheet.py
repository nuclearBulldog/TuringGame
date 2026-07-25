import pygame
import pytest

from turing_game.systems import spritesheet


def _make_sheet(cols, rows, frame_w, frame_h):
    """Build a sheet where each cell is a solid, uniquely tinted block."""
    sheet = pygame.Surface((cols * frame_w, rows * frame_h), pygame.SRCALPHA)
    for r in range(rows):
        for c in range(cols):
            colour = (c * 40 % 256, r * 40 % 256, 100)
            sheet.fill(colour, (c * frame_w, r * frame_h, frame_w, frame_h))
    return sheet


def _save(sheet, tmp_path, name='sheet.png'):
    path = tmp_path / name
    pygame.image.save(sheet, str(path))
    return path


def test_load_sheet_returns_surface_of_expected_size(tmp_path):
    path = _save(_make_sheet(4, 3, 32, 48), tmp_path)
    surface = spritesheet.load_sheet(path)
    assert isinstance(surface, pygame.Surface)
    assert surface.get_size() == (128, 144)


def test_slice_grid_returns_row_major_frames_of_fixed_size(tmp_path):
    sheet = _make_sheet(4, 3, 32, 48)
    frames = spritesheet.slice_grid(sheet, 32, 48)
    assert len(frames) == 12
    assert all(frame.get_size() == (32, 48) for frame in frames)
    # Row-major: frame 0 is top-left cell, frame 4 is start of second row.
    assert frames[0].get_at((0, 0))[:3] == (0, 0, 100)
    assert frames[4].get_at((0, 0))[:3] == (0, 40, 100)


def test_load_states_maps_states_to_correct_frame_counts(tmp_path):
    path = _save(_make_sheet(4, 3, 32, 48), tmp_path)
    layout = {
        'idle': (0, 0, 2),   # row 0, first 2 cols
        'run': (1, 0, 4),    # row 1, all 4 cols
        'jump': (2, 0, 1),   # row 2, first col
    }
    states = spritesheet.load_states(path, 32, 48, layout)
    assert set(states) == {'idle', 'run', 'jump'}
    assert [len(states[s]) for s in ('idle', 'run', 'jump')] == [2, 4, 1]
    assert all(f.get_size() == (32, 48) for frames in states.values() for f in frames)


def test_load_states_reads_from_the_requested_row(tmp_path):
    path = _save(_make_sheet(4, 3, 32, 48), tmp_path)
    states = spritesheet.load_states(path, 32, 48, {'run': (1, 0, 4)})
    # Row 1 cells are tinted green-channel 40.
    assert states['run'][0].get_at((0, 0))[:3] == (0, 40, 100)


def test_slice_grid_rejects_frame_larger_than_sheet(tmp_path):
    sheet = _make_sheet(1, 1, 16, 16)
    with pytest.raises(ValueError):
        spritesheet.slice_grid(sheet, 32, 32)
