"""
Web entry point for pygbag/WebAssembly builds.
Drives the same Game class as main.py but with an async loop required by pygbag.
Run with: python -m pygbag turing-game/main_web.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

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


asyncio.run(main())
