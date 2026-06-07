import pygame
import csv
import settings

class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))


class TileMap:
    """Converts a text grid into tiles and spawn points."""

    def __init__(self, level_path):
        self.tiles = pygame.sprite.Group()
        self.tile_size = 16
        assets_dir = settings.ASSETS_DIR

        self.dirt_img = pygame.image.load(assets_dir / "dirt-block.png").convert_alpha()
        pygame.transform.scale(self.dirt_img, (16, 16))

        self.grass_img = pygame.image.load(assets_dir / "grass-block.png").convert_alpha()
        pygame.transform.scale(self.grass_img, (16, 16))


        self.level_data = self._load_level(level_path)

        self.player_spawn = (100, 100)
        self.enemy_spawns = []

        self._build_world()

    def _load_level(self, path):
        data = []

        with open(path) as file:
            reader = csv.reader(file, delimiter=',')
            for row in reader:
                data.append([int(tile) for tile in row])
        return data

    def _build_world(self):
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

                elif tile == 3:
                    self.enemy_spawns.append((x * self.tile_size, y * self.tile_size))


    def draw(self, screen, camera):
        for tile in self.tiles:
            screen.blit(tile.image, camera.apply(tile))


