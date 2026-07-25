# TuringGame

A platformer with turn based battles about the **ethical use of AI**. Explore the overworld, walk into an AI-ethics dilemma, and
fight it out as a turn based encounter where your choices are the moves.

Built with Python 3.11 + pygame.

[![CI](https://github.com/nuclearBulldog/TuringGame/actions/workflows/ci.yml/badge.svg)](https://github.com/nuclearBulldog/TuringGame/actions/workflows/ci.yml)

![TuringGame gameplay](docs/demo.gif)

| Overworld | Battle |
|---|---|
| ![Overworld](docs/screenshots/overworld.png) | ![Battle](docs/screenshots/battle_report_due.png) |

---

## Quickstart

Requires **Python 3.11** and **git**.

```bash
git clone https://github.com/nuclearBulldog/TuringGame.git
cd TuringGame
python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m turing_game
```

<details>
<summary>Installing Python 3.11 on Linux</summary>

```bash
sudo apt install git python3.11        # Debian/Ubuntu
sudo dnf install git python3.11        # Fedora
sudo pacman -S git python              # Arch
```
</details>

> The Windows commands are untested as I do not have a Windows machine. If something
> is off there please create an issue or PR.

**Controls** ~ `A`/`D` or arrows to move, `Space`/`W`/`Up` to jump, arrows + `Enter`
to pick a battle move, `M` to mute, `Esc` to back out.

---

## How it's built

The design goal was to keep **game rules, presentation, and content** independent of
each other, so each can be tested or changed without touching the other two.

![TuringGame module architecture](docs/architecture.drawio.svg)

### Layout

```
turing_game/
├── engine/     StateManager, Camera            framework, no game rules
├── states/     MainMenu, Overworld, Battle…    one class per screen
├── systems/    BattleSystem, sprites, audio    rules and asset loading
├── entities/   Player, Enemy                   physics and collision
├── world/      Level, TileMap                  level loading and persistence
├── ui/         BattleUI, ImageButton           drawing only
├── assets/     sprite sheets, font, audio
└── data/       levels (CSV) and encounters (JSON)
tests/          mirrors the package, runs headless
tools/          placeholder-art generator
```

---

## Development

```bash
pip install -r requirements-dev.txt
```

```bash
pytest                                    # 125 tests, headless: no window or audio device
ruff check turing_game tests tools        # lint
pytest --cov=turing_game --cov-report=term-missing
```

CI runs lint and the full suite on every push and PR, and fails the build if coverage
drops below 85%.

The suite runs entirely headless via SDL's dummy drivers, which is why the sheet loader
in [`spritesheet.py`](turing_game/systems/spritesheet.py) falls back to an unconverted
surface when no display exists.

### Regenerating placeholder art

```bash
python tools/gen_placeholder_art.py
```

Existing sheets are skipped, because several have since been replaced with hand-drawn
art. Pass `--force` only if you mean to overwrite them.

---

## Licence

MIT see [LICENSE.txt](LICENSE.txt).
