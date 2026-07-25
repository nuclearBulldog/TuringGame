"""Global configuration values used across the project."""
from pathlib import Path

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / 'assets'
DATA_DIR = BASE_DIR / 'data'
LEVEL_DIR = DATA_DIR / 'levels'
ENCOUNTER_DIR = DATA_DIR / 'encounters'

BASE_FONT = ASSETS_DIR / 'monogram.ttf'
BG_MUSIC = ASSETS_DIR / 'main-theme.wav'


WIDTH = 960
HEIGHT = 580
FPS = 60
TITLE = 'TuringGame'

# World / physics
GRAVITY = 1800
PLAYER_SPEED = 220
PLAYER_JUMP_VELOCITY = -650
ENEMY_SPEED = 120
# Camera smoothing
CAMERA_LERP = 0.12

# Colours
SKY = (112, 197, 255)
WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
RED = (210, 70, 70)
YELLOW = (255, 215, 50)
BLUE = (70, 110, 210)
PANEL = (235, 235, 235)
HP_GREEN = (50, 180, 70)
HP_RED = (190, 70, 70)
OUTLINE = (30, 30, 30)

# --- dawnbringer-32 palette subset (assets/colours/dawnbringer-32.pal) ---
# Named so battle/overworld draw code never hard-codes an RGB literal.
DB_INK = (34, 32, 52)
DB_SLATE = (50, 60, 57)
DB_DGRAY = (89, 86, 82)
DB_MGRAY = (105, 106, 106)
DB_PALE = (203, 219, 252)
DB_WHITE = (255, 255, 255)
DB_SKY = (99, 155, 255)
DB_YELLOW = (251, 242, 54)
DB_ORANGE = (223, 113, 38)
DB_GREEN = (106, 190, 48)
DB_RED = (217, 87, 99)

# UI roles for the battle scene, all sourced from the palette above.
UI_FRAME = DB_INK          # window / creature-panel outline
UI_TEXT = DB_INK           # body text
UI_PANEL = DB_PALE         # window fill
UI_PANEL_EDGE = DB_WHITE   # inner bevel highlight
UI_HINT = DB_SLATE         # secondary hint text (darker than mid-gray for legibility on pale)
MOVE_SELECT_FILL = DB_YELLOW
MOVE_SELECT_EDGE = DB_ORANGE
MOVE_IDLE_FILL = DB_PALE
HP_TRACK = DB_DGRAY
HP_FILL_HIGH = DB_GREEN
HP_FILL_LOW = DB_RED
HIT_FLASH = DB_WHITE       # tint colour for the damage flash
