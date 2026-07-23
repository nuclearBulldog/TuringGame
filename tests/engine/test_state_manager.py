import pygame
from engine.state_manager import StateManager


class MockState:
    def __init__(self):
        self.entered = False
        self.exited = False
        self.updated_dt = 0
        self.drawn = False
        self.handled_events = None

    def on_enter(self):
        self.entered = True

    def on_exit(self):
        self.exited = True

    def update(self, dt):
        self.updated_dt = dt

    def draw(self, screen):
        self.drawn = True

    def handle_events(self, events):
        self.handled_events = events

class MockGame:
    pass

def test_state_manager_init():
    game = MockGame()
    sm = StateManager(game)
    assert sm.game == game
    assert sm.state is None

def test_state_manager_change():
    game = MockGame()
    sm = StateManager(game)
    state1 = MockState()
    state2 = MockState()

    sm.change(state1)
    assert sm.state == state1
    assert state1.entered is True
    assert state1.exited is False

    sm.change(state2)
    assert sm.state == state2
    assert state1.exited is True
    assert state2.entered is True

def test_state_manager_delegation():
    game = MockGame()
    sm = StateManager(game)
    state = MockState()
    sm.change(state)

    sm.update(0.16)
    assert state.updated_dt == 0.16

    sm.draw(None)
    assert state.drawn is True

    events = [pygame.event.Event(pygame.QUIT)]
    sm.handle_events(events)
    assert state.handled_events == events
