# AI Contributions — WebAssembly Web Port

**Branch:** `feature/web-wasm`  
**Date:** 2026-07-10  
**Model:** Claude Sonnet 4.6  
**Task:** Add pygbag WebAssembly support so TuringGame runs in a web browser (Apache2 / EC2), without modifying any existing game code.

---

## Files Created

### `turing-game/main_web.py`
Async entry point required by pygbag. Drives the existing `Game` class by
replicating the body of `Game.run()` with `await asyncio.sleep(0)` at each
frame — a WebAssembly scheduling requirement. `game.py` is not touched.

Build command:
```bash
python -m pygbag turing-game/main_web.py
```

### `docs/apache2-wasm-setup.md`
Step-by-step deployment guide covering:
- Building the static bundle with pygbag
- `scp` transfer to EC2
- Apache2 `application/wasm` MIME type configuration
- Cross-Origin-Opener-Policy / Cross-Origin-Embedder-Policy headers
  (required by browsers for `SharedArrayBuffer`, which pygbag depends on)
- Known limitations (`.wav`/`.mid` audio, pygame-menu WASM quirks)

---

## Files Modified

### `requirements.txt`
Added:
```
pygbag~=0.9.0
```

---

## Files Not Modified (by design)

| File | Reason |
|---|---|
| `turing-game/game.py` | Core game logic — constraint: untouched |
| `turing-game/main.py` | Desktop entry point — must keep working |
| `turing-game/settings.py` | Global config — no changes needed |
| `tests/` | No test changes in scope |

---

## Design Decisions

**Why `main_web.py` instead of modifying `main.py`?**  
pygbag requires an `async def main()` loop, which is incompatible with the
synchronous `while self.running:` loop in `Game.run()`. Creating a separate
entry point keeps `main.py` working for desktop play with zero changes.

**Why replicate the loop body instead of calling `game.run()`?**  
`game.run()` is a blocking synchronous loop — calling it from an async function
would block the WebAssembly event loop entirely. The async wrapper accesses
`game`'s public attributes (`game.running`, `game.clock`, `game.state_manager`,
`game.screen`) to drive each frame, then yields control with `await asyncio.sleep(0)`.

**Why `pygbag~=0.9.0`?**  
Pinned to a compatible minor version to avoid breaking API changes in future
pygbag releases while still allowing patch-level fixes.

---

## Known Risks

- **Audio:** `.wav` and `.mid` formats have inconsistent browser support under
  WASM. If music is silent, convert to `.ogg`.
- **pygame-menu:** Threading constraints in WASM can affect menu behaviour.
  Test the main menu screen after deploying.
