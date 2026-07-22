import pytest
from world.tilemap import TileMap


def _write_level(tmp_path):
    # tile codes: 0/1 solid, 2 player spawn, 3 enemy spawn, -1 empty
    rows = [
        [-1, -1, -1],
        [-1, 2, 3],
        [0, 0, 0],
    ]
    path = tmp_path / "level.csv"
    path.write_text("\n".join(",".join(str(code) for code in row) for row in rows))
    return path


def test_tilemap_tiles_scaled_to_tile_size(tmp_path):
    # Regression: scale() result was discarded, leaving tiles unscaled.
    tilemap = TileMap(_write_level(tmp_path))
    assert tilemap.dirt_img.get_size() == (tilemap.tile_size, tilemap.tile_size)
    assert tilemap.grass_img.get_size() == (tilemap.tile_size, tilemap.tile_size)


def test_tilemap_parses_spawns(tmp_path):
    tilemap = TileMap(_write_level(tmp_path))
    ts = tilemap.tile_size
    assert tilemap.player_spawn == (1 * ts, 1 * ts)
    assert (2 * ts, 1 * ts) in tilemap.enemy_spawns


def test_tilemap_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        TileMap(tmp_path / "does_not_exist.csv")
