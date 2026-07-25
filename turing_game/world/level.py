"""A mutable, persistent level.

The overworld used to rebuild itself on every enemy collision, which meant
defeated enemies came back and no progress could be tracked. ``Level`` owns the
world state that must survive the Overworld -> Battle -> BattleResult ->
Overworld round trip: the tile map, the player, the live enemies, the set of
cleared encounters, and the running score.
"""
from __future__ import annotations

import random
from pathlib import Path

from turing_game import settings
from turing_game.entities.enemy import Enemy
from turing_game.entities.player import Player
from turing_game.systems import encounter_data
from turing_game.world.tilemap import TileMap


class Level:
    def __init__(self, level_path: Path | str) -> None:
        self.tilemap = TileMap(level_path)
        px, py = self.tilemap.player_spawn
        self.player = Player(px, py)
        self.enemies = [
            Enemy(
                spawn.x, spawn.y,
                encounter_id=spawn.encounter_id,
                sprite_key=encounter_data.sprite_for(spawn.encounter_id),
            )
            for spawn in self.tilemap.enemy_spawns
        ]
        self.cleared_encounters = set()
        self.total_score = 0

    @classmethod
    def load_random(cls, rng: random.Random | None = None) -> Level:
        """Build a level from a randomly chosen ``level*.csv`` in the level dir.

        Injecting ``rng`` keeps selection deterministic under test; production
        callers use the module-level :mod:`random`.
        """
        paths = sorted(settings.LEVEL_DIR.glob('level*.csv'))
        if not paths:
            raise FileNotFoundError(f'No level files found in {settings.LEVEL_DIR}')
        chooser = rng if rng is not None else random
        return cls(chooser.choice(paths))

    def clear_encounter(self, enemy: Enemy, score: int) -> None:
        """Permanently remove a defeated enemy and bank its score.

        Idempotent: a second call for an already-cleared enemy is a no-op, so a
        stray resume can't double-count or raise.
        """
        if enemy not in self.enemies:
            return
        self.enemies.remove(enemy)
        self.cleared_encounters.add(enemy.encounter_id)
        self.total_score += score
