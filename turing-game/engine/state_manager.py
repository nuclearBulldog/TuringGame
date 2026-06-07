class StateManager:
    """ holds only one active state at a time! """

    def __init__(self, game):
        self.game = game
        self.state = None

    def change(self, new_state):
        if self.state and hasattr(self.state, 'on_exit'):
            self.state.on_exit()

        self.state = new_state

        if self.state and hasattr(self.state, 'on_enter'):
            self.state.on_enter()

    def update(self, dt):
        self.state.update(dt)

    def draw(self, screen):
        self.state.draw(screen)

    def handle_events(self, events):
        self.state.handle_events(events)
