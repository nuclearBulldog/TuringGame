"""Generate themed placeholder sprite sheets for TuringGame.

Every colour is an index into assets/colours/dawnbringer-32.pal. Real art later
replaces these PNGs 1:1 against the grid documented in assets/README.md.
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((8, 8))

# tools/ sits at the repo root; assets live under turing-game/assets.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "turing-game", "assets")
PAL_PATH = os.path.join(ASSETS, "colours", "dawnbringer-32.pal")


def load_palette(path):
    with open(path, encoding="utf-8") as fh:
        lines = [ln.strip() for ln in fh if ln.strip()]
    count = int(lines[2])
    pal = []
    for ln in lines[3:3 + count]:
        r, g, b = (int(v) for v in ln.split())
        pal.append((r, g, b))
    return pal


PAL = load_palette(PAL_PATH)
# Friendly names -> palette index (see dawnbringer-32).
C = {
    "black": 0, "ink": 1, "dpurple": 2, "brown": 3, "mbrown": 4,
    "orange": 5, "tan": 6, "skin": 7, "yellow": 8, "lime": 9,
    "green": 10, "teal": 11, "dgreen": 12, "olive": 13, "slate": 14,
    "indigo": 15, "blue": 16, "peri": 17, "sky": 18, "cyan": 19,
    "pale": 20, "white": 21, "ltgray": 22, "gray": 23, "mgray": 24,
    "dgray": 25, "purple": 26, "dred": 27, "red": 28, "pink": 29,
    "yellowgreen": 30, "dgold": 31,
}


def col(name):
    return PAL[C[name]]


def px(surf, x, y, name, w=1, h=1):
    surf.fill(col(name), (x, y, w, h))


# ----------------------------------------------------------------------------
# PLAYER  — a student in a hoodie. Frame 32x48, 4 cols x 3 rows.
# row0 idle(2), row1 run(4), row2 jump(1)
# ----------------------------------------------------------------------------
def draw_student(step, jump=False):
    """step drives leg/arm swing; returns a 32x48 SRCALPHA frame."""
    s = pygame.Surface((32, 48), pygame.SRCALPHA)
    bob = 1 if step in (1, 3) else 0
    top = 6 + bob

    # hair + head
    px(s, 11, top - 2, "ink", 10, 4)          # hair
    px(s, 12, top + 1, "skin", 8, 7)          # face
    px(s, 14, top + 4, "ink", 1, 1)           # eye
    px(s, 18, top + 4, "ink", 1, 1)           # eye
    # hoodie torso
    px(s, 9, top + 8, "blue", 14, 14)
    px(s, 9, top + 8, "indigo", 14, 2)        # hood shoulders shade
    px(s, 15, top + 8, "indigo", 2, 14)       # zip
    # backpack strap
    px(s, 11, top + 9, "orange", 2, 12)

    if jump:
        # arms up, legs tucked
        px(s, 6, top + 6, "blue", 3, 6)
        px(s, 23, top + 6, "blue", 3, 6)
        px(s, 11, top + 22, "indigo", 5, 8)
        px(s, 16, top + 22, "indigo", 5, 8)
        px(s, 11, top + 29, "orange", 5, 3)   # shoes
        px(s, 16, top + 29, "mbrown", 5, 3)
        pygame.draw.rect(s, col("ink"), (9, top + 8, 14, 14), 1)
        return s

    # arms
    swing = {0: 0, 1: 2, 2: 0, 3: -2}[step]
    px(s, 6, top + 9 + swing, "blue", 3, 9)
    px(s, 23, top + 9 - swing, "blue", 3, 9)
    # legs with running swing
    la = {0: 0, 1: 3, 2: 0, 3: -3}[step]
    px(s, 11, top + 22, "indigo", 4, 14 - abs(la))
    px(s, 17, top + 22, "indigo", 4, 14 - abs(la))
    px(s, 11 - (la if la > 0 else 0), top + 34 - abs(la), "orange", 5, 3)
    px(s, 17 + (-la if la < 0 else 0), top + 34 - abs(la), "mbrown", 5, 3)
    pygame.draw.rect(s, col("ink"), (9, top + 8, 14, 14), 1)
    return s


def build_player():
    sheet = pygame.Surface((128, 144), pygame.SRCALPHA)
    idle = [draw_student(0), draw_student(1)]
    run = [draw_student(0), draw_student(1), draw_student(2), draw_student(3)]
    jump = [draw_student(0, jump=True)]
    for i, f in enumerate(idle):
        sheet.blit(f, (i * 32, 0))
    for i, f in enumerate(run):
        sheet.blit(f, (i * 32, 48))
    for i, f in enumerate(jump):
        sheet.blit(f, (i * 32, 96))
    return sheet


# ----------------------------------------------------------------------------
# ENEMIES — 32x44 frames, 4 cols x 5 rows. Each row = one sprite key with a
# 4-frame loop (idle samples cols 0-1, run samples cols 0-3).
# ----------------------------------------------------------------------------
def frame_surface():
    return pygame.Surface((32, 44), pygame.SRCALPHA)


def enemy_report_due(step):
    """A looming stack of paper with a red DUE band + ticking clock."""
    s = frame_surface()
    wob = {0: 0, 1: 1, 2: 0, 3: -1}[step]
    # paper stack
    for i, y in enumerate(range(40, 10, -5)):
        w = 22 - i
        x = 16 - w // 2 + (wob if i % 2 else 0)
        px(s, x, y, "white", w, 5)
        px(s, x, y + 4, "ltgray", w, 1)
        pygame.draw.rect(s, col("gray"), (x, y, w, 5), 1)
    # red DUE band
    px(s, 6, 22, "red", 20, 5)
    px(s, 8, 24, "white", 2, 1)
    px(s, 12, 24, "white", 2, 1)
    px(s, 16, 24, "white", 2, 1)
    px(s, 20, 24, "white", 2, 1)
    # clock on top
    px(s, 12, 4 + wob, "yellow", 8, 8)
    pygame.draw.rect(s, col("ink"), (12, 4 + wob, 8, 8), 1)
    px(s, 16, 6 + wob, "ink", 1, 3)
    px(s, 16, 8 + wob, "ink", 3, 1)
    return s


def enemy_deepfake(step):
    """A glitching human face, RGB-split scanlines."""
    s = frame_surface()
    off = {0: 0, 1: 2, 2: -2, 3: 1}[step]
    px(s, 9, 8, "skin", 14, 20)             # face
    px(s, 11, 4, "ink", 10, 5)              # hair
    px(s, 12, 14, "white", 3, 3)            # eyes
    px(s, 18, 14, "white", 3, 3)
    px(s, 13, 15, "ink", 1, 1)
    px(s, 19, 15, "ink", 1, 1)
    px(s, 13, 22, "dred", 6, 1)             # mouth
    # glitch bands (RGB split)
    px(s, 9 + off, 12, "cyan", 14, 2)
    px(s, 9 - off, 18, "pink", 14, 2)
    px(s, 9 + off, 24, "sky", 14, 1)
    # neck/shoulders
    px(s, 8, 28, "indigo", 16, 12)
    return s


def enemy_hiring_filter(step):
    """A funnel/sieve rejecting little applicant dots out the side."""
    s = frame_surface()
    # funnel body
    pygame.draw.polygon(s, col("mgray"), [(4, 8), (28, 8), (20, 26), (12, 26)])
    pygame.draw.polygon(s, col("ink"), [(4, 8), (28, 8), (20, 26), (12, 26)], 1)
    px(s, 14, 26, "mgray", 4, 12)          # spout
    px(s, 8, 11, "dgray", 16, 2)           # sieve slot
    # applicant dots dropping in
    for i in range(4):
        px(s, 8 + i * 4, 3 + ((step + i) % 3), "sky", 2, 2)
    # rejected dot flung to the side (red)
    rx = {0: 24, 1: 26, 2: 28, 3: 25}[step]
    px(s, rx, 18, "red", 2, 2)
    # accepted dot from spout
    px(s, 15, 38 + (step % 2), "lime", 2, 2)
    return s


def enemy_exam_proctor(step):
    """A surveillance webcam / AI eye with a blinking record light."""
    s = frame_surface()
    px(s, 6, 12, "slate", 20, 16)          # camera body
    pygame.draw.rect(s, col("ink"), (6, 12, 20, 16), 1)
    px(s, 13, 6, "dgray", 6, 6)            # mount
    px(s, 15, 2, "dgray", 2, 4)
    # lens
    look = {0: 0, 1: 1, 2: 2, 3: 1}[step]
    px(s, 11, 16, "cyan", 10, 8)
    pygame.draw.rect(s, col("ink"), (11, 16, 10, 8), 1)
    px(s, 14 + look, 18, "ink", 3, 4)      # pupil scans
    px(s, 15 + look, 18, "white", 1, 1)
    # record light blinks
    if step % 2 == 0:
        px(s, 23, 13, "red", 2, 2)
    # stand
    px(s, 14, 28, "dgray", 4, 12)
    px(s, 9, 39, "dgray", 14, 2)
    return s


def enemy_study_bot(step):
    """An overconfident study robot with a big grin on a screen face."""
    s = frame_surface()
    bob = {0: 0, 1: 1, 2: 0, 3: 1}[step]
    y = 6 + bob
    px(s, 7, y, "ltgray", 18, 16)          # head
    pygame.draw.rect(s, col("ink"), (7, y, 18, 16), 1)
    px(s, 9, y + 2, "sky", 14, 12)         # screen
    px(s, 11, y + 5, "white", 3, 3)        # eyes (confident)
    px(s, 18, y + 5, "white", 3, 3)
    px(s, 12, y + 6, "ink", 1, 1)
    px(s, 19, y + 6, "ink", 1, 1)
    px(s, 11, y + 10, "white", 10, 1)      # grin
    px(s, 11, y + 9, "white", 1, 1)
    px(s, 20, y + 9, "white", 1, 1)
    # antenna
    px(s, 15, y - 3, "ink", 1, 3)
    px(s, 14, y - 5, "yellow", 3, 3)
    # body + arms (thumbs up)
    px(s, 10, y + 17, "mgray", 12, 12)
    px(s, 22, y + 15, "ltgray", 3, 6)      # raised arm
    px(s, 23, y + 12, "yellow", 2, 3)      # thumb
    px(s, 12, y + 29, "dgray", 4, 6)
    px(s, 16, y + 29, "dgray", 4, 6)
    return s


ENEMY_BUILDERS = [
    ("report_due", enemy_report_due),
    ("deepfake_classmate", enemy_deepfake),
    ("hiring_filter", enemy_hiring_filter),
    ("exam_proctor", enemy_exam_proctor),
    ("study_bot", enemy_study_bot),
]


def build_enemies():
    sheet = pygame.Surface((128, 220), pygame.SRCALPHA)
    for row, (_key, builder) in enumerate(ENEMY_BUILDERS):
        for step in range(4):
            sheet.blit(builder(step), (step * 32, row * 44))
    return sheet


# ----------------------------------------------------------------------------
# BATTLE BACKDROP — 960x580 campus / classroom.
# ----------------------------------------------------------------------------
def build_battle_bg():
    s = pygame.Surface((960, 580))
    s.fill(col("pale"))                      # upper wall
    px(s, 0, 0, "sky", 960, 70)              # ceiling band
    px(s, 0, 300, "tan", 960, 280)           # floor
    px(s, 0, 296, "mbrown", 960, 6)          # floor trim
    # chalkboard on the wall
    px(s, 250, 70, "dgreen", 460, 150)
    pygame.draw.rect(s, col("mbrown"), (250, 70, 460, 150), 6)
    for i, (tx, tw) in enumerate([(280, 120), (430, 90), (560, 120)]):
        px(s, tx, 110 + i * 30, "pale", tw, 3)   # chalk scribbles
    px(s, 300, 160, "white", 90, 3)
    px(s, 300, 175, "white", 140, 3)
    # window with daylight (left)
    px(s, 40, 90, "cyan", 150, 110)
    pygame.draw.rect(s, col("white"), (40, 90, 150, 110), 6)
    px(s, 113, 90, "white", 4, 110)
    px(s, 40, 140, "white", 150, 4)
    # window (right)
    px(s, 770, 90, "cyan", 150, 110)
    pygame.draw.rect(s, col("white"), (770, 90, 150, 110), 6)
    px(s, 843, 90, "white", 4, 110)
    px(s, 770, 140, "white", 150, 4)
    # a couple of desks in the mid-ground
    for dx in (150, 640):
        px(s, dx, 250, "dgold", 120, 16)
        px(s, dx + 8, 266, "brown", 10, 34)
        px(s, dx + 100, 266, "brown", 10, 34)
    # standing pads under each combatant (enemy top-right, player mid-left)
    pygame.draw.ellipse(s, col("mbrown"), (580, 150, 210, 40))
    pygame.draw.ellipse(s, col("mbrown"), (90, 300, 250, 55))
    return s


# ----------------------------------------------------------------------------
# HP BAR FRAME — 132x16 single frame; in-code fill sits in the track.
# Track inset documented in README: 3px border all round.
# ----------------------------------------------------------------------------
def build_hp():
    s = pygame.Surface((132, 16), pygame.SRCALPHA)
    px(s, 0, 0, "ink", 132, 16)              # outer border
    px(s, 1, 1, "mgray", 130, 14)            # bevel
    px(s, 3, 3, "dgray", 126, 10)            # empty track
    px(s, 3, 3, "slate", 126, 2)             # track top shade
    return s


def save(surf, name):
    path = os.path.join(ASSETS, name)
    pygame.image.save(surf, path)
    print(f"wrote {name:16} {surf.get_width()}x{surf.get_height()}")


save(build_player(), "player.png")
save(build_enemies(), "enemies.png")
save(build_battle_bg(), "battle_bg.png")
save(build_hp(), "hp.png")
print("done")
