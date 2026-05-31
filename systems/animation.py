# AI Generated BoilerPlate

class AnimationController:
    """Stores named animations and advances frames for the active state."""

    def __init__(self, animations, fps_by_state=None):
        self.animations = animations
        self.fps_by_state = fps_by_state or {name: 6 for name in animations}
        self.current = next(iter(animations))
        self.frame_index = 0.0

    def set_state(self, state_name):
        if state_name != self.current:
            self.current = state_name
            self.frame_index = 0.0

    def update(self, dt):
        frames = self.animations[self.current]
        if len(frames) <= 1:
            return
        fps = self.fps_by_state.get(self.current, 6)
        self.frame_index = (self.frame_index + fps * dt) % len(frames)

    def image(self):
        return self.animations[self.current][int(self.frame_index)]
