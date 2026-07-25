from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from turing_game.engine.camera import Camera

import csv
from collections import namedtuple

import pygame

from turing_game import settings
from turing_game.systems import encounter_data

# An enemy placement resolved from the level grid: pixel position plus the
# encounter id its spawn tile is bound to.
EnemySpawn = namedtuple('EnemySpawn', ['x', 'y', 'encounter_id'])


class Tile(pygame.sprite.Sprite):
    def __init__(self, image: pygame.Surface, x: int, y: int) -> None:
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))


class TileMap:
    """Converts a text grid into tiles and spawn points."""

    def __init__(self, level_path: Path | str) -> None:
        self.tiles = pygame.sprite.Group()
        self.tile_size = 16
        assets_dir = settings.ASSETS_DIR

        self.dirt_img = pygame.image.load(assets_dir / "dirt-block.png").convert_alpha()
        self.dirt_img = pygame.transform.scale(self.dirt_img, (self.tile_size, self.tile_size))

        self.grass_img = pygame.image.load(assets_dir / "grass-block.png").convert_alpha()
        self.grass_img = pygame.transform.scale(self.grass_img, (self.tile_size, self.tile_size))

        self.level_data = self._load_level(level_path)

        self.player_spawn = (100, 100)
        self.enemy_spawns = []
        self.goal_rect = None
        self._spawn_tile_ids = encounter_data.spawn_tile_map()

        self._build_world()

    def _load_level(self, path: Path | str) -> list[list[int]]:
        data = []

        try:
            with open(path, newline='', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=',')
                for row in reader:
                    data.append([int(tile) for tile in row])
        except FileNotFoundError as error:
            raise FileNotFoundError(f'Level file not found: {path}') from error
        except ValueError as error:
            raise ValueError(f'Level file {path} contains a non-integer tile: {error}') from error
        return data

    def _build_world(self) -> None:
        for y, row in enumerate(self.level_data):
            for x, tile in enumerate(row):

                if tile == 0 or tile == 1:
                    if y > 0 and self.level_data[y - 1][x] == -1:
                        img = self.grass_img

                    else:
                        img = self.dirt_img

                    self.tiles.add(Tile(img, x * self.tile_size, y * self.tile_size))

                elif tile == 2:
                    self.player_spawn = (x * self.tile_size, y * self.tile_size)

                elif tile == 4:
                    self.goal_rect = pygame.Rect(
                        x * self.tile_size, y * self.tile_size,
                        self.tile_size, self.tile_size,
                    )

                elif tile in self._spawn_tile_ids:
                    self.enemy_spawns.append(EnemySpawn(
                        x * self.tile_size,
                        y * self.tile_size,
                        self._spawn_tile_ids[tile],
                    ))

    def draw(self, screen: pygame.Surface, camera: Camera) -> None:
        for tile in self.tiles:
            screen.blit(tile.image, camera.apply(tile))
