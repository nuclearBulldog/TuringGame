import pygame
from pathlib import Path
import os
"""Global configuration values used across the project."""

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
TILE_SIZE = 32
GRAVITY = 1800
PLAYER_SPEED = 220
PLAYER_JUMP_VELOCITY = -650
ENEMY_SPEED = 120
# Camera smoothing
CAMERA_LERP = 0.12

# Colours
SKY = (112, 197, 255)
GROUND = (90, 90, 95)
POLE = (0, 0, 0)
FLAG = (50, 255, 90)
WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
RED = (210, 70, 70)
YELLOW = (255, 215, 50)
BLUE = (70, 110, 210)
PANEL = (235, 235, 235)
HP_GREEN = (50, 180, 70)
HP_RED = (190, 70, 70)
OUTLINE = (30, 30, 30)

DEBUG = False
