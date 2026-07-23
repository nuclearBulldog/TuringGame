import asyncio

import pytest
import pygame
from game import Game
import settings

def test_game_init(monkeypatch):
    # Mock pygame.display.set_mode to return a simple surface
    monkeypatch.setattr(pygame.display, "set_mode", lambda size: pygame.Surface(size))
    
    game = Game()
    
    assert game.running is True
    assert game.state_manager is not None
    assert game.state_manager.state.__class__.__name__ == "MainMenu"

def test_game_quit_event(monkeypatch):
    monkeypatch.setattr(pygame.display, "set_mode", lambda size: pygame.Surface(size))
    
    # Mock pygame.event.get to return a QUIT event
    def mock_get():
        return [pygame.event.Event(pygame.QUIT)]
    monkeypatch.setattr(pygame.event, "get", mock_get)
    
    # Mock flip so it doesn't do anything
    monkeypatch.setattr(pygame.display, "flip", lambda: None)
    
    game = Game()
    
    # This should run one iteration and exit because running becomes False
    asyncio.run(game.run())
    
    assert game.running is False
