"""Load fixed-grid sprite sheets into per-state frame lists.

The sole job here is turning a PNG laid out on a uniform grid into the
``{state: [Surface, ...]}`` shape that :class:`~systems.animation.AnimationController`
already consumes. Nothing here touches the controller or assumes a display exists,
so it runs headless under the test harness.
"""
from __future__ import annotations

from pathlib import Path

import pygame


def load_sheet(path: Path | str) -> pygame.Surface:
    """Load a sheet PNG, converting for fast blitting when a display exists.

    ``convert_alpha`` needs an initialised display surface; in headless contexts
    without one we return the raw loaded surface so callers still get pixels.
    """
    surface = pygame.image.load(str(path))
    if pygame.display.get_init() and pygame.display.get_surface() is not None:
        return surface.convert_alpha()
    return surface


def slice_grid(sheet: pygame.Surface, frame_w: int, frame_h: int) -> list[pygame.Surface]:
    """Cut ``sheet`` into row-major frames of ``frame_w`` x ``frame_h``.

    Raises:
        ValueError: if a single frame is larger than the sheet in either axis.
    """
    sheet_w, sheet_h = sheet.get_size()
    if frame_w > sheet_w or frame_h > sheet_h:
        raise ValueError(
            f'Frame {frame_w}x{frame_h} does not fit in sheet {sheet_w}x{sheet_h}'
        )

    cols = sheet_w // frame_w
    rows = sheet_h // frame_h

    frames = []
    for row in range(rows):
        for col in range(cols):
            rect = pygame.Rect(col * frame_w, row * frame_h, frame_w, frame_h)
            frames.append(sheet.subsurface(rect).copy())
    return frames


def load_states(
    path: Path | str,
    frame_w: int,
    frame_h: int,
    layout: dict[str, tuple[int, int, int]],
) -> dict[str, list[pygame.Surface]]:
    """Return ``{state: [frame, ...]}`` sliced from the sheet at ``path``.

    ``layout`` maps each state name to a ``(row, start_col, count)`` triple. The
    caller picks the state names, so they line up with whatever keys
    ``AnimationController`` is initialised with (e.g. ``idle``/``run``/``jump``).
    """
    sheet = load_sheet(path)
    grid = slice_grid(sheet, frame_w, frame_h)
    cols = sheet.get_width() // frame_w

    states = {}
    for state, (row, start_col, count) in layout.items():
        start = row * cols + start_col
        states[state] = grid[start:start + count]
    return states
