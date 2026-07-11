"""
Single entry point for TuringGame — desktop and browser.

pygbag (WebAssembly) runs `main.py` by default and requires the game loop to be
async so it can yield to the browser's event loop. The same async loop runs fine
on desktop via asyncio.run(), so one file serves both and no generated
index.html ever needs patching.
"""
import asyncio
import os
import sys

# Vendored pure-Python deps (e.g. pygame_menu) live here for the web build, where
# pygbag cannot fetch from PyPI at runtime. On desktop the real installs take
# precedence, so appending this path is harmless.
sys.path.append(os.path.join(os.path.dirname(__file__), "vendor"))

import pygame
import settings
from game import Game


async def main():
    game = Game()
    while game.running:
        dt = game.clock.tick(settings.FPS) / 1000.0

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                game.running = False

        game.state_manager.handle_events(events)
        game.state_manager.update(dt)
        game.state_manager.draw(game.screen)

        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
