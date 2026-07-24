"""
Single entry point for TuringGame.

The game loop itself lives in Game.run(); it is async and is driven here by
asyncio.run().
"""
import asyncio

from game import Game

if __name__ == "__main__":
    asyncio.run(Game().run())
