# Build: WebAssembly Web Port via pygbag

## Task
Add pygbag WebAssembly support so the TuringGame pygame application can run in a
web browser, served by Apache2 on an EC2 instance, without modifying any existing
game code.

## Context
- Tech stack: Python, pygame 2.6.1, pygame-menu 4.5.2
- Entry point: `turing-game/main.py` (imports and runs `Game` from `game.py`)
- Game logic lives in: `turing-game/game.py`, `turing-game/settings.py`
- All work happens on a **new git branch** — create it before making any changes
- pygbag compiles a pygame project to WebAssembly; it requires the game loop to be
  `async` and call `await asyncio.sleep(0)` each frame. This is a WebAssembly
  scheduling constraint, not a game logic change.

## Requirements
1. Create a new git branch (e.g. `feature/web-wasm`) before any changes.
2. Add `pygbag` to `requirements.txt`.
3. Create a new `turing-game/main_web.py` that provides the async entry point
   pygbag expects — it wraps the existing `Game` class, does NOT modify it.
4. The async wrapper must call `await asyncio.sleep(0)` inside the game loop so
   the browser's event loop can breathe.
5. Run `python -m pygbag turing-game/` (or point it at `main_web.py`) to produce
   the static build output (default: `build/web/`).
6. Document the Apache2 configuration needed to serve the output correctly,
   including the `application/wasm` MIME type for `.wasm` files.

## Constraints
- Do NOT modify: `turing-game/game.py`, `turing-game/main.py`,
  `turing-game/settings.py`, `tests/`, or any test file.
- Do NOT change the game's logic, rendering, or input handling.
- `main.py` must continue to work for local desktop play (`python main.py`).
- Follow the existing project structure — new files go inside `turing-game/`.

## Acceptance Criteria
- [ ] A new git branch exists with all changes committed to it.
- [ ] `python -m pygbag turing-game/` (pointing at `main_web.py`) completes
  without errors and produces a `build/web/` directory.
- [ ] Opening `build/web/index.html` in a local browser (or via `python -m
  pygbag --serve`) loads and plays the game.
- [ ] `python turing-game/main.py` still launches the desktop version unchanged.
- [ ] `requirements.txt` lists pygbag with a pinned or compatible version.
- [ ] A short `docs/apache2-wasm-setup.md` (or README section) explains the
  Apache2 MIME type config and how to deploy `build/web/` to the EC2 instance.
