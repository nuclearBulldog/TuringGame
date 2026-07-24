"""Shared loader for the encounter database.

Both the battle system and the world's tile map need to read
``data/encounters/encounters.json``. Centralising the read here keeps their
error handling identical and gives the tile map the spawn-tile bindings without
duplicating file access.
"""
import json

import settings


def load_encounters():
    """Return the parsed encounter database.

    Raises:
        FileNotFoundError: if the encounters file is missing.
        ValueError: if the file is not valid JSON.
    """
    data_path = settings.ENCOUNTER_DIR / 'encounters.json'

    try:
        with open(data_path, encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError as error:
        raise FileNotFoundError(f'Encounter data file not found: {data_path}') from error
    except json.JSONDecodeError as error:
        raise ValueError(
            f'Encounter data file is not valid JSON ({data_path}): {error}'
        ) from error


def sprite_for(encounter_id, database=None):
    """Return the sprite key declared by an encounter, or ``None`` if unset.

    Keeps the ``"sprite"`` binding in the encounter JSON as the single source of
    truth; callers pass the result to :class:`~entities.enemy.Enemy`.
    """
    if database is None:
        database = load_encounters()
    encounter = database.get(encounter_id) or {}
    return encounter.get('sprite')


def spawn_tile_map(database=None):
    """Map each encounter's optional ``spawn_tile`` id to its encounter id.

    Encounters without a ``spawn_tile`` are skipped, so a scenario is only
    placeable in a level once it opts in by declaring one.
    """
    if database is None:
        database = load_encounters()

    mapping = {}
    for encounter_id, encounter in database.items():
        tile_id = encounter.get('spawn_tile')
        if tile_id is not None:
            mapping[tile_id] = encounter_id
    return mapping
