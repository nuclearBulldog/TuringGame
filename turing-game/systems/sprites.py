"""Game-specific bindings from a sprite key to a sheet, grid and rows.

`systems.spritesheet` is the generic slicer; this module knows *which* sheet and
row each character uses. Both the overworld entities and the battle scene import
from here so the sheet layout has a single source of truth (mirrored in
``assets/README.md``).
"""
import settings
from systems import spritesheet

PLAYER_SHEET = settings.ASSETS_DIR / 'player.png'
ENEMY_SHEET = settings.ASSETS_DIR / 'enemies.png'
BATTLE_BG = settings.ASSETS_DIR / 'battle_bg.png'
HP_FRAME = settings.ASSETS_DIR / 'hp.png'

PLAYER_FRAME = (32, 48)
ENEMY_FRAME = (32, 44)

PLAYER_LAYOUT = {'idle': (0, 0, 2), 'run': (1, 0, 4), 'jump': (2, 0, 1)}

# Row index into enemies.png per sprite key (see assets/README.md).
ENEMY_ROWS = {
    'report_due': 0,
    'deepfake_classmate': 1,
    'hiring_filter': 2,
    'exam_proctor': 3,
    'study_bot': 4,
}
DEFAULT_ENEMY_SPRITE = 'report_due'


def resolve_enemy_sprite(sprite_key, encounter_id=None):
    """Pick a valid enemy sprite key, degrading gracefully.

    Prefers an explicit ``sprite_key``; falls back to the ``encounter_id`` when it
    happens to name a sprite (handy for directly-constructed test enemies); else
    the default. Guarantees the return value is always a key in ``ENEMY_ROWS``.
    """
    if sprite_key in ENEMY_ROWS:
        return sprite_key
    if encounter_id in ENEMY_ROWS:
        return encounter_id
    return DEFAULT_ENEMY_SPRITE


def load_player_states():
    fw, fh = PLAYER_FRAME
    return spritesheet.load_states(PLAYER_SHEET, fw, fh, PLAYER_LAYOUT)


def load_enemy_states(sprite_key):
    row = ENEMY_ROWS.get(sprite_key, ENEMY_ROWS[DEFAULT_ENEMY_SPRITE])
    fw, fh = ENEMY_FRAME
    layout = {'idle': (row, 0, 2), 'run': (row, 0, 4)}
    return spritesheet.load_states(ENEMY_SHEET, fw, fh, layout)


def player_battle_frame():
    """Single idle frame used for the player creature in battle."""
    return load_player_states()['idle'][0]


def enemy_battle_frame(sprite_key):
    """Single idle frame used for the enemy creature in battle."""
    return load_enemy_states(resolve_enemy_sprite(sprite_key))['idle'][0]
