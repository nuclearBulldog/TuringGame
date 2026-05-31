import pygame

# AI Generated BoilerPlate

class SoundManager:
    """Centralised audio manager with safe fallback if mixer fails."""

    def __init__(self):
        self.available = False
        self.muted = False
        self.sounds = {}
        try:
            pygame.mixer.init()
            self.available = True
        except pygame.error:
            self.available = False

    def load_sound(self, name, path):
        if not self.available:
            return
        try:
            self.sounds[name] = pygame.mixer.Sound(path)
        except pygame.error:
            pass

    def play(self, name):
        if not self.available or self.muted:
            return
        sound = self.sounds.get(name)
        if sound:
            sound.play()

    def toggle_mute(self):
        self.muted = not self.muted
        if self.available:
            pygame.mixer.music.set_volume(0.0 if self.muted else 1.0)
            for sound in self.sounds.values():
                sound.set_volume(0.0 if self.muted else 1.0)
