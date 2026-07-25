"""Single entry point for TuringGame.

Run with ``python -m turing_game`` (or the ``turing-game`` console script after
an install). The game loop itself lives in :meth:`Game.run`; it is async and is
driven here by ``asyncio.run()``.
"""
import asyncio

from turing_game.game import Game


def main() -> None:
    """Start the game. Referenced by the ``turing-game`` console script."""
    asyncio.run(Game().run())


if __name__ == "__main__":
    main()
