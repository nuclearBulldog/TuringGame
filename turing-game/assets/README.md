# Art assets - sprite-sheet spec

The game loads characters and battle art from fixed-grid PNGs via
`systems/spritesheet.py`. The placeholder PNGs here were generated with pygame
(`scratchpad/gen_art.py`) using only colours from `colours/dawnbringer-32.pal`.

**Swapping in real art is a pure file swap.** Keep each file's pixel dimensions,
grid, frame order, and per-row meaning exactly as documented below and no code
changes are needed. Transparent background (`SRCALPHA`) for the character sheets;
`battle_bg.png` and `hp.png` may be opaque.

## `player.png` - 128 × 144

- Frame size: **32 × 48**, grid **4 columns × 3 rows** (row-major).
- Row → animation state (state names must match the `AnimationController` keys
  in `entities/player.py`):

  | Row | State | Frames used | Cells |
  |-----|-------|-------------|-------|
  | 0   | `idle`| 2           | cols 0–1 |
  | 1   | `run` | 4           | cols 0–3 |
  | 2   | `jump`| 1           | col 0    |

- Feet rest near the bottom of the frame; character faces **right** (the engine
  flips horizontally for left-facing movement).

## `enemies.png` - 128 × 220

- Frame size: **32 × 44**, grid **4 columns × 5 rows** (row-major).
- Each **row is one enemy**, keyed by the encounter's `"sprite"` field in
  `data/encounters/encounters.json`. Row order is fixed:

  | Row | Sprite key            | Concept (placeholder)              |
  |-----|-----------------------|------------------------------------|
  | 0   | `report_due`          | Leaning paper tower + deadline band + clock |
  | 1   | `deepfake_classmate`  | Ordinary classmate face + a synthetic tell  |
  | 2   | `misinformation`      | Reply bubble with a flip-flopping verify badge |
  | 3   | `exam_proctor`        | Ceiling camera that is mostly lens          |
  | 4   | `study_bot`           | Grinning thumbs-up study robot              |

- Within each row: `idle` samples cols 0–1, `run` samples cols 0–3. Provide a
  4-frame loop per row. Enemies face **left** by default (engine flips for
  right-facing movement in the overworld).

To add a new enemy: append a row here, add a `"sprite"` entry to the encounter,
and grow the sheet to `128 × (44 × rows)`. `Enemy` falls back to `report_due`
if a sprite key is missing.

## `battle_bg.png` - 960 × 580

- Full-screen battle backdrop (campus/classroom). The bottom ~160 px is covered
  by the battle HUD at runtime. Two darker oval "pads" mark where the combatants
  stand: enemy top-right (~centre 685, 170), player mid-left (~centre 215, 327).

## `hp.png` - 132 × 16

- Single-frame HP-bar **frame**: a 3 px border on all sides around an empty
  track. The coloured fill is drawn in code inside the track (inset 3 px), so the
  frame art only needs border + empty groove. Scaled horizontally to each bar's
  width at runtime.

## Regenerating placeholders

```bash
.venv/bin/python tools/gen_placeholder_art.py   # rewrites the four PNGs above
```
