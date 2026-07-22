"""
Single entry point for TuringGame — desktop and browser.

pygbag (WebAssembly) runs `main.py` and requires the game loop to be async so it
can yield to the browser's event loop each frame. The same async loop runs fine
on desktop via asyncio.run(), so one entry point serves both — the loop itself
lives in Game.run().
"""
import asyncio
import os
import sys

# Vendored pure-Python deps (e.g. pygame_menu) live here for the web build, where
# pygbag cannot fetch from PyPI at runtime. On desktop the real installs take
# precedence, so appending this path is harmless.
sys.path.append(os.path.join(os.path.dirname(__file__), "vendor"))

from game import Game

if __name__ == "__main__":
    asyncio.run(Game().run())
