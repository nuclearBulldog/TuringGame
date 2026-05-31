class BaseState:
    def __init__(self, manager):
        self.manager = manager
        self.game = manager.game

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def update(self, dt):
        pass

    def draw(self, screen):
        pass

    def handle_events(self, events):
        pass



