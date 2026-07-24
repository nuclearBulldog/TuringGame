"""A mutable, persistent level.

The overworld used to rebuild itself on every enemy collision, which meant
defeated enemies came back and no progress could be tracked. ``Level`` owns the
world state that must survive the Overworld -> Battle -> BattleResult ->
Overworld round trip: the tile map, the player, the live enemies, the set of
cleared encounters, and the running score.
"""
import random

import settings
from entities.enemy import Enemy
from entities.player import Player
from world.tilemap import TileMap


class Level:
    def __init__(self, level_path):
        self.tilemap = TileMap(level_path)
        px, py = self.tilemap.player_spawn
        self.player = Player(px, py)
        self.enemies = [
            Enemy(spawn.x, spawn.y, encounter_id=spawn.encounter_id)
            for spawn in self.tilemap.enemy_spawns
        ]
        self.cleared_encounters = set()
        self.total_score = 0

    @classmethod
    def load_random(cls, rng=None):
        """Build a level from a randomly chosen ``level*.csv`` in the level dir.

        Injecting ``rng`` keeps selection deterministic under test; production
        callers use the module-level :mod:`random`.
        """
        paths = sorted(settings.LEVEL_DIR.glob('level*.csv'))
        if not paths:
            raise FileNotFoundError(f'No level files found in {settings.LEVEL_DIR}')
        chooser = rng if rng is not None else random
        return cls(chooser.choice(paths))

    def clear_encounter(self, enemy, score):
        """Permanently remove a defeated enemy and bank its score.

        Idempotent: a second call for an already-cleared enemy is a no-op, so a
        stray resume can't double-count or raise.
        """
        if enemy not in self.enemies:
            return
        self.enemies.remove(enemy)
        self.cleared_encounters.add(enemy.encounter_id)
        self.total_score += score
