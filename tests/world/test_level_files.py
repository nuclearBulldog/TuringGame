"""Integrity checks over the shipped level CSVs and encounter data.

These guard the hand-generated levels: every level must be loadable, have a
player start and a reachable goal, place only enemy tiles that bind to real
encounters, and sit on unbroken bedrock so the player can never fall out of the
world.
"""
import csv

import pytest

from turing_game import settings
from turing_game.systems import encounter_data

MARKER_TILES = {2, 3, 4, 5, 6, 7, 8}
SOLID = {0, 1}
ROWS = 44


def _level_paths():
    return sorted(settings.LEVEL_DIR.glob('level*.csv'))


def _load(path):
    with open(path, newline='', encoding='utf-8') as f:
        return [[int(v) for v in row] for row in csv.reader(f)]


def test_there_are_multiple_levels():
    assert len(_level_paths()) >= 2


@pytest.mark.parametrize('path', _level_paths(), ids=lambda p: p.name)
def test_level_shape_and_markers(path):
    grid = _load(path)
    assert len(grid) == ROWS, f'{path.name} should have {ROWS} rows'
    widths = {len(r) for r in grid}
    assert len(widths) == 1, f'{path.name} rows are ragged: {widths}'

    flat = [v for row in grid for v in row]
    assert flat.count(2) == 1, f'{path.name} needs exactly one player spawn'
    assert flat.count(4) == 1, f'{path.name} needs exactly one goal tile'

    spawn_ids = set(encounter_data.spawn_tile_map())
    enemy_tiles = [v for v in flat if v in MARKER_TILES and v not in (2, 4)]
    assert enemy_tiles, f'{path.name} has no encounter spawns'
    for tile in enemy_tiles:
        assert tile in spawn_ids, f'{path.name} tile {tile} maps to no encounter'


@pytest.mark.parametrize('path', _level_paths(), ids=lambda p: p.name)
def test_level_has_bedrock(path):
    grid = _load(path)
    assert all(v in SOLID for v in grid[-1]), f'{path.name} bottom row must be solid'


@pytest.mark.parametrize('path', _level_paths(), ids=lambda p: p.name)
def test_markers_stand_on_solid_ground(path):
    grid = _load(path)
    height = len(grid)
    for y, row in enumerate(grid):
        for x, tile in enumerate(row):
            if tile in MARKER_TILES:
                assert y + 1 < height, f'{path.name} marker at bottom edge'
                assert grid[y + 1][x] in SOLID, (
                    f'{path.name} marker {tile} at ({x},{y}) floats'
                )


def test_all_declared_encounters_are_reachable():
    # Every encounter that opts into a spawn tile should appear in some level,
    # so no authored scenario is stranded.
    placed = set()
    for path in _level_paths():
        placed.update(v for row in _load(path) for v in row if v in MARKER_TILES)
    for tile, encounter_id in encounter_data.spawn_tile_map().items():
        assert tile in placed, f'encounter {encounter_id} (tile {tile}) is unreachable'
