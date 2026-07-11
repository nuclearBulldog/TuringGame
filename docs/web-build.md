# Web build (pygbag / WebAssembly)

The game runs in the browser via [pygbag](https://pygame-web.github.io/), which
compiles the pygame app to WebAssembly. Both `turing-game/build/` and
`turing-game/vendor/` are **generated** and are git-ignored — regenerate them
with the steps below.

## 1. Vendor the pure-Python dependencies

`battle_result.py` uses `pygame_menu`, which pygbag cannot fetch at runtime
(the browser blocks the PyPI request via CORS). So `pygame_menu` and its
pure-Python deps are vendored into `turing-game/vendor/` and shipped inside the
build archive. `pygame` itself is provided by pygbag and must **not** be vendored.

```bash
python -m pip install --no-deps --target turing-game/vendor \
    pygame-menu pyperclip typing_extensions
```

`turing-game/main.py` adds `vendor/` to `sys.path` so the lazy
`import pygame_menu` resolves from the bundle.

## 2. Build

```bash
cd turing-game
python -m pygbag --build .
```

Output lands in `turing-game/build/web/` (`index.html`, `turing-game.tar.gz`,
`turing-game.apk`, `favicon.png`).

## 3. Serve / deploy

Deploy the contents of `turing-game/build/web/` to any static host
(GitHub Pages, itch.io, Netlify). On a real origin, pygbag's dev-mode CDN
rewrite does not trigger, so it loads cleanly.

## 4. Site wrapper (custom HTML/CSS around the game)

`turing-game/site/index.html` is a hand-authored landing page that embeds the
game in an `<iframe>`. Because pygbag regenerates its own `index.html` on every
build, keep your HTML/CSS here instead — it is never overwritten. Edit it freely.

Deploy = wrapper + a copy of the game build in `site/game/` (git-ignored):

```bash
cd turing-game
rm -rf site/game && mkdir -p site/game && cp -R build/web/. site/game/
# then deploy the whole site/ folder
```

Preview locally by serving `site/` from a port that does NOT start with 8
(pygbag's dev-mode CDN rewrite fires on `localhost:8xxx`):

```bash
cd turing-game/site && python -m http.server 7654   # then open http://localhost:7654
```

## Known gotchas

- **Entry point:** pygbag runs `main.py` by default. `main.py` uses an async
  game loop (`asyncio.run(main())`) so it works both under WASM (which requires
  yielding to the browser event loop) and on desktop — so the generated
  `index.html` needs **no** patching. Do not reintroduce a separate `main_web.py`;
  that is what forced the fragile template edits.
- **BrowserFS:** the pygbag 0.9.3 template loads `browserfs.min.js` from a CDN
  path that 404s, logging `BrowserFS not found`. This is a non-fatal warning —
  the game still runs. If it ever matters, point the tag at
  `https://cdn.jsdelivr.net/npm/browserfs@2/dist/browserfs.min.js` via a custom
  pygbag template (not a post-build edit, which gets regenerated).
- **Audio:** `assets/main-theme.wav` is not WASM-compatible; convert to OGG or
  pygbag's serve mode errors (bypass with `--disable-sound-format-error`).
- **Local testing:** pygbag's dev mode rewrites the package CDN to
  `localhost:8000` when served from a `localhost:8xxx` port, which can stall the
  loader if no pygbag server is providing that CDN. Deploying to a real host
  avoids this.
