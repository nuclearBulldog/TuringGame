import pygame

# AI Generated BoilerPlate

import pygame


class SoundManager:
    """Centralised audio manager with safe fallback if mixer fails."""

    def __init__(self):
        self.available = False
        self.muted = False
        self.sounds = {}

        # 1. Store your target background volume here (0.75 = 75%)
        self.music_volume = 0.75

        try:
            pygame.mixer.init()
            self.available = True
        except pygame.error:
            self.available = False

    def load_sound(self, name, path):
        if not self.available: return
        try:
            self.sounds[name] = pygame.mixer.Sound(path)
        except pygame.error:
            pass

    def play(self, name, loops=0):
        if not self.available or self.muted: return
        sound = self.sounds.get(name)
        if sound:
            sound.play(loops=loops)

    def play_music(self, path, loops=-1):
        """Streams a background WAV file. Loops infinitely at 75% volume."""
        if not self.available:
            return

        try:
            pygame.mixer.music.load(str(path))

            # 2. Apply the volume before starting playback
            pygame.mixer.music.set_volume(0.0 if self.muted else self.music_volume)

            # 3. Play with infinite looping (loops=-1)
            pygame.mixer.music.play(loops)

        except pygame.error as e:
            print(f"Could not load music track: {e}")

    def stop_music(self):
        """Stops the active background music stream."""
        if self.available:
            pygame.mixer.music.stop()

    def toggle_mute(self):
        self.muted = not self.muted
        if self.available:
            # 4. Ensure unmuting returns to 75%, NOT 100% (1.0)
            pygame.mixer.music.set_volume(0.0 if self.muted else self.music_volume)

            # Sound effects can stay at default 1.0 volume unless you want to tie them to a variable too
            for sound in self.sounds.values():
                sound.set_volume(0.0 if self.muted else 1.0)