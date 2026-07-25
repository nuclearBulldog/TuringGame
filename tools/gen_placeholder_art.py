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


# Shading ramps: dark -> light runs that already exist inside dawnbringer-32.
# Picking neighbours from one ramp keeps highlights and shadows in the palette's
# own hue family instead of drifting to an arbitrary lighter RGB.
RAMPS = {
    "denim": ("ink", "indigo", "blue", "peri", "sky"),
    "flesh": ("brown", "mbrown", "tan", "skin"),
    "steel": ("ink", "dgray", "mgray", "gray", "ltgray", "pale"),
    "paper": ("gray", "ltgray", "pale", "white"),
    "alarm": ("dpurple", "dred", "red", "pink"),
    "screen": ("indigo", "blue", "sky", "cyan"),
    "foliage": ("olive", "dgreen", "green", "lime"),
    "amber": ("brown", "dgold", "orange", "yellow"),
}


def shade(ramp, base, step):
    """Step along a ramp from ``base``, clamped at both ends.

    ``step`` is +1 for a highlight, -1 for a shadow. Clamping means a caller can
    ask for a highlight on an already-lightest colour without special-casing.
    """
    names = RAMPS[ramp]
    i = names.index(base)
    return names[max(0, min(len(names) - 1, i + step))]


def box(surf, x, y, w, h, ramp, base):
    """A filled rect with a lit top edge and a shadowed bottom edge.

    Three rows of value is the cheapest way to make a flat rectangle read as a
    solid object; without it sprites dissolve when scaled up in the battle scene.
    """
    px(surf, x, y, base, w, h)
    px(surf, x, y, shade(ramp, base, 1), w, 1)
    if h > 2:
        px(surf, x, y + h - 1, shade(ramp, base, -1), w, 1)


def outline(surf, name="ink"):
    """Wrap a frame in a 1 px contour derived from its own alpha channel.

    Rather than hand-drawing a border per shape, this reads the silhouette back
    off the surface and stamps a dark copy one pixel out in each direction. Any
    sprite gets a consistent contour for free, and it keeps working when the
    shapes underneath change. Returns a new surface; the original is untouched.
    """
    silhouette = pygame.mask.from_surface(surf).to_surface(
        setcolor=col(name), unsetcolor=(0, 0, 0, 0))
    ringed = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        ringed.blit(silhouette, (dx, dy))
    ringed.blit(surf, (0, 0))
    return ringed


# ----------------------------------------------------------------------------
# PLAYER  — a student in a hoodie. Frame 32x48, 4 cols x 3 rows.
# row0 idle(2), row1 run(4), row2 jump(1)
# ----------------------------------------------------------------------------
# A 4-frame run: contact, passing-low, contact (mirrored), passing-high. Each
# entry is (body lift, front-leg reach, back-leg reach) in pixels; the arms swing
# opposite the legs so the pose reads as a stride rather than a hop.
RUN_CYCLE = [
    (0, 4, -3),
    (-1, 1, 1),
    (0, -3, 4),
    (1, 1, 1),
]


def draw_leg(s, x, y, reach, shoe, tone="indigo"):
    """One leg planted at ``x``; ``reach`` swings the foot fore (+) or aft (-).

    ``tone`` carries the depth cue: the far leg is drawn a step darker down the
    denim ramp, which is what keeps two adjacent limbs from reading as one wide
    trouser block once the contour merges them.
    """
    thigh = 8 - abs(reach) // 3
    shin = 5 - abs(reach) // 4
    px(s, x, y, tone, 4, thigh)
    foot_x = x + reach
    px(s, foot_x, y + thigh, tone, 4, shin)
    px(s, foot_x - 1, y + thigh + shin, shoe, 6, 3)


def draw_student(step, jump=False):
    """A student in a hoodie with a backpack strap; 32x48 SRCALPHA frame.

    ``step`` indexes RUN_CYCLE. The same routine serves idle (steps 0 and 3, which
    read as a gentle weight shift) and run (all four), so the character can never
    drift out of proportion between its two animation states.
    """
    s = pygame.Surface((32, 48), pygame.SRCALPHA)
    lift, front, back = RUN_CYCLE[step]
    top = 7 + lift

    # head — hair sits proud of the face so the silhouette has a readable crown
    px(s, 11, top, "ink", 10, 5)
    px(s, 10, top + 2, "ink", 1, 3)
    px(s, 12, top + 4, "skin", 8, 7)
    px(s, 12, top + 4, "tan", 8, 1)                  # brow in shadow under hair
    px(s, 19, top + 5, "tan", 1, 6)                  # cheek turns away from light
    px(s, 17, top + 7, "ink", 2, 2)                  # facing right: one eye reads
    px(s, 14, top + 7, "ink", 1, 2)
    px(s, 16, top + 10, "mbrown", 3, 1)              # mouth

    torso_y = top + 11
    if jump:
        # tucked: arms up, knees drawn in, whole body a compact diamond
        box(s, 10, torso_y, 13, 13, "denim", "blue")
        px(s, 10, torso_y, "indigo", 13, 3)          # hood bunches at the shoulders
        px(s, 15, torso_y + 3, "indigo", 2, 10)      # zip
        px(s, 12, torso_y + 1, "orange", 2, 11)      # backpack strap
        px(s, 7, torso_y - 4, "blue", 3, 8)          # arms thrown up
        px(s, 23, torso_y - 4, "blue", 3, 8)
        px(s, 11, torso_y + 13, "indigo", 5, 7)
        px(s, 17, torso_y + 13, "indigo", 5, 7)
        px(s, 10, torso_y + 20, "orange", 6, 3)
        px(s, 17, torso_y + 20, "orange", 6, 3)
        return outline(s)

    box(s, 10, torso_y, 13, 14, "denim", "blue")
    px(s, 10, torso_y, "indigo", 13, 3)              # hood bunches at the shoulders
    px(s, 15, torso_y + 3, "indigo", 2, 11)          # zip
    px(s, 12, torso_y + 1, "orange", 2, 12)          # backpack strap
    px(s, 21, torso_y + 4, "peri", 1, 8)             # lit edge, light from the right

    # arms counter-swing against the legs
    px(s, 7, torso_y + 3 - back, "blue", 3, 9)
    px(s, 23, torso_y + 3 - front, "blue", 3, 9)
    px(s, 7, torso_y + 11 - back, "skin", 3, 2)      # hands
    px(s, 23, torso_y + 11 - front, "skin", 3, 2)

    legs_y = torso_y + 14
    draw_leg(s, 11, legs_y, back, "brown", tone=shade("denim", "indigo", -1))
    draw_leg(s, 17, legs_y, front, "orange")
    px(s, 20, legs_y, "peri", 1, 6)                  # lit edge on the near leg
    return outline(s)


def build_player():
    sheet = pygame.Surface((128, 144), pygame.SRCALPHA)
    # Idle borrows the two passing poses: feet together, differing only in body
    # lift, so standing still reads as breathing instead of a half-frozen stride.
    idle = [draw_student(3), draw_student(1)]
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
    """A leaning tower of paper with a red deadline band and a ticking clock."""
    s = frame_surface()
    wob = {0: 0, 1: 1, 2: 0, 3: -1}[step]
    # Sheets stack bottom-up and each one leans a little further, so the tower
    # looks like it is about to go over rather than sitting neatly squared.
    for i, y in enumerate(range(38, 12, -5)):
        w = 24 - i * 2
        x = 16 - w // 2 + (wob if i % 2 else -wob)
        box(s, x, y, w, 5, "paper", "pale")
        px(s, x, y + 4, "gray", w, 1)            # shadow cast on the sheet below
    # deadline band wrapping the stack
    px(s, 4, 24, "red", 24, 6)
    px(s, 4, 24, "pink", 24, 1)
    px(s, 4, 29, "dred", 24, 1)
    for tick in range(6, 28, 5):                 # stamped lettering, unreadable
        px(s, tick, 26, "white", 3, 2)
    # clock perched on top, hands sweeping round the frames
    hand = [(0, -3), (2, -2), (3, 0), (2, 2)][step]
    px(s, 11, 2 + wob, "yellow", 10, 10)
    px(s, 11, 2 + wob, "white", 10, 1)
    px(s, 11, 11 + wob, "dgold", 10, 1)
    px(s, 15, 6 + wob, "ink", 2, 2)              # pivot
    px(s, 16 + hand[0], 7 + wob + hand[1], "ink", 1, 2)
    px(s, 10, 1 + wob, "dgold", 2, 2)            # bells
    px(s, 20, 1 + wob, "dgold", 2, 2)
    return outline(s)


def draw_classmate_base(s, step):
    """The believable half: an ordinary classmate, drawn straight.

    Everything here is deliberately unremarkable — a face the player would scroll
    past. The sprite only works if this part is convincing first, because the
    horror of a deepfake is that it looks fine until you notice what is wrong.
    """
    px(s, 8, 6, "brown", 16, 6)                  # hair
    px(s, 8, 6, "mbrown", 16, 2)
    px(s, 9, 10, "skin", 14, 18)                 # face
    px(s, 9, 10, "tan", 14, 1)                   # brow shadow under the fringe
    px(s, 21, 12, "tan", 2, 14)                  # cheek turning from the light
    px(s, 12, 15, "white", 3, 3)                 # eyes
    px(s, 18, 15, "white", 3, 3)
    px(s, 13, 16, "ink", 2, 2)
    px(s, 19, 16, "ink", 2, 2)
    px(s, 14, 23, "dred", 5, 2)                  # mouth
    px(s, 15, 28, "tan", 6, 3)                   # neck
    box(s, 6, 30, 20, 12, "denim", "indigo")     # shoulders
    px(s, 14, 30, "blue", 4, 12)                 # collar


def deepfake_tell(s, step):
    """Draw whatever marks this face as synthetic. One frame of a 4-frame loop.

    `s` is a 32x44 SRCALPHA surface with `draw_classmate_base` already drawn on
    it, so this only adds the tell on top. `step` is 0-3; make the tell change
    across those four frames or the sprite will sit dead still in battle.

    Available helpers:
        px(s, x, y, "colour", w, h)   filled rect, colour is a dawnbringer name
        box(s, x, y, w, h, ramp, base)   filled rect with lit top / dark bottom
        shade(ramp, base, +1 or -1)   step along a ramp for a highlight/shadow

    Useful landmarks in the base: face spans x 9-22, y 10-27; eyes sit at y 15-17;
    the mouth is at y 23; shoulders start at y 30.

    TODO(caleb): implement the tell. See the notes in the chat for the trade-off
    between a glitch read, a seam/mask read, and an uncanny-symmetry read.
    """
    return


def enemy_deepfake(step):
    """A classmate whose face is not theirs."""
    s = frame_surface()
    draw_classmate_base(s, step)
    deepfake_tell(s, step)
    return outline(s)


def enemy_misinformation(step):
    """A confident chatbot answer whose 'verified' badge keeps flipping to false.

    The silhouette reads as a reply bubble; the tell is instability. On alternate
    frames a citation line glows red (a fact it made up) and the corner badge
    flips from a green tick to a red cross — the answer looks sourced and certain
    and is neither. That flicker is the whole point of the sprite.
    """
    s = frame_surface()
    lie = step % 2 == 0

    # reply bubble with a tail pointing down toward the "speaker"
    pygame.draw.rect(s, col("pale"), (3, 3, 26, 27), border_radius=5)
    px(s, 5, 4, "white", 22, 2)                   # top edge catches the light
    px(s, 5, 27, "ltgray", 22, 2)                 # base falls into shadow
    pygame.draw.polygon(s, col("pale"), [(8, 28), (16, 28), (9, 37)])
    px(s, 9, 28, "ltgray", 2, 7)

    # lines of answer text; the second is a fabricated claim that flickers red
    px(s, 7, 9, "slate", 18, 2)
    px(s, 7, 13, "red" if lie else "gray", 16, 2)
    px(s, 7, 13, "pink" if lie else "ltgray", 16, 1)
    px(s, 7, 17, "slate", 20, 2)
    px(s, 7, 21, "gray", 10, 2)                    # trailing citation stub...
    px(s, 19, 21, "sky", 5, 2)                     # ...that links nowhere real

    # corner badge: green tick when it happens to be right, red cross when not
    base, sheen = ("red", "pink") if lie else ("green", "lime")
    pygame.draw.circle(s, col(base), (25, 7), 5)
    pygame.draw.circle(s, col(sheen), (24, 6), 2)
    if lie:
        pygame.draw.line(s, col("white"), (22, 4), (28, 10), 1)
        pygame.draw.line(s, col("white"), (28, 4), (22, 10), 1)
    else:
        pygame.draw.lines(s, col("white"), False, [(22, 7), (24, 9), (28, 4)], 1)
    return outline(s)


def enemy_exam_proctor(step):
    """A ceiling camera that is mostly lens — an eye that never blinks.

    The housing is deliberately small and the aperture huge: at battle scale the
    only thing that has to survive is the pupil tracking you across the frames.
    """
    s = frame_surface()
    # ceiling mount
    px(s, 6, 0, "dgray", 20, 3)
    px(s, 6, 0, "mgray", 20, 1)
    px(s, 14, 3, "dgray", 4, 5)

    # housing shell
    pygame.draw.ellipse(s, col("gray"), (3, 7, 26, 26))
    pygame.draw.ellipse(s, col("ltgray"), (5, 9, 20, 10))     # top catches light
    pygame.draw.ellipse(s, col("mgray"), (5, 22, 22, 9))      # underside in shadow

    # aperture, then the pupil sweeping left to right and back
    pygame.draw.ellipse(s, col("ink"), (8, 12, 16, 16))
    pygame.draw.ellipse(s, col("cyan"), (9, 13, 14, 14))
    pygame.draw.ellipse(s, col("sky"), (10, 17, 12, 9))       # iris shades downward
    look = [-3, 0, 3, 0][step]
    px(s, 14 + look, 17, "ink", 4, 6)                          # pupil
    px(s, 15 + look, 18, "white", 1, 2)                        # catchlight

    # record light — on for three frames in four, so it reads as barely blinking
    if step != 2:
        px(s, 24, 9, "red", 3, 3)
        px(s, 24, 9, "pink", 3, 1)
    else:
        px(s, 24, 9, "dred", 3, 3)
    return outline(s)


def enemy_study_bot(step):
    """A study robot that is cheerfully, confidently wrong.

    The grin never changes across the cycle; only the thumb pumps. Unwavering
    friendliness is the tell — it is the sprite for an assistant that answers
    just as brightly whether or not it knows.
    """
    s = frame_surface()
    bob = [0, 1, 2, 1][step]
    y = 5 + bob

    # antenna with a pulsing tip
    px(s, 15, y - 5, "mgray", 2, 5)
    tip = ["yellow", "white", "yellow", "dgold"][step]
    px(s, 13, y - 8, tip, 5, 4)

    # head casing
    box(s, 6, y, 20, 17, "steel", "ltgray")
    px(s, 8, y + 2, "indigo", 16, 13)                # screen bezel
    px(s, 9, y + 3, "sky", 14, 11)                   # screen
    px(s, 9, y + 3, "cyan", 14, 2)                   # scanline glare across the top
    px(s, 11, y + 6, "white", 4, 4)                  # wide, guileless eyes
    px(s, 18, y + 6, "white", 4, 4)
    px(s, 12, y + 7, "ink", 2, 2)
    px(s, 19, y + 7, "ink", 2, 2)
    px(s, 11, y + 12, "white", 11, 1)                # fixed grin
    px(s, 10, y + 11, "white", 1, 1)
    px(s, 22, y + 11, "white", 1, 1)

    # chassis
    box(s, 9, y + 18, 14, 12, "steel", "mgray")
    px(s, 13, y + 21, "lime", 6, 3)                  # all-clear status lamp
    # arm pumping a thumbs-up
    lift = [0, 1, 2, 1][step]
    px(s, 23, y + 16 - lift, "ltgray", 3, 7)
    px(s, 23, y + 12 - lift, "yellow", 3, 4)
    px(s, 6, y + 19, "ltgray", 3, 7)                 # far arm hangs
    # treads
    px(s, 8, y + 30, "dgray", 16, 4)
    px(s, 8, y + 30, "mgray", 16, 1)
    return outline(s)


ENEMY_BUILDERS = [
    ("report_due", enemy_report_due),
    ("deepfake_classmate", enemy_deepfake),
    ("misinformation", enemy_misinformation),
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
    # standing pads under each combatant, aligned to the battle-scene anchors in
    # ui/battle_ui.py (enemy right of its panel, player lower-left).
    pygame.draw.ellipse(s, col("mbrown"), (600, 192, 170, 34))   # enemy feet ~ (685, 209)
    pygame.draw.ellipse(s, col("mbrown"), (92, 322, 182, 34))    # player feet ~ (183, 339)
    return s


# ----------------------------------------------------------------------------
# HP BAR FRAME — 132x16 single frame; in-code fill sits in the track.
# Track inset documented in README: 3px border all round.
# ----------------------------------------------------------------------------
def build_hp():
    """A recessed groove: lit on the bottom-right, shadowed on the top-left.

    The bevel runs opposite to a raised button on purpose — light falling from
    above hits the *far* wall of a hollow, which is what sells the track as cut
    into the panel rather than sitting on it. The 3 px inset is load-bearing:
    ``BattleUI.draw_hp_bar`` fills the track at exactly that offset.
    """
    s = pygame.Surface((132, 16), pygame.SRCALPHA)
    px(s, 0, 0, "ink", 132, 16)              # outer contour
    px(s, 1, 1, "gray", 130, 14)             # frame face
    px(s, 1, 1, "ltgray", 130, 1)            # frame catches the light on top
    px(s, 1, 14, "dgray", 130, 1)            # and falls away underneath

    px(s, 3, 3, "ink", 126, 10)              # empty track
    px(s, 3, 3, "dgray", 126, 1)             # near wall in shadow
    px(s, 3, 3, "dgray", 1, 10)
    px(s, 3, 12, "mgray", 126, 1)            # far wall catches light
    px(s, 128, 3, "mgray", 1, 10)
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
