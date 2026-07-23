import pygame


class SoundManager:
    """Centralised audio manager with safe fallback if mixer fails."""

    def __init__(self):
        self.available = False
        self.muted = False
        self.music_volume = 0.75

        try:
            pygame.mixer.init()
            self.available = True
        except pygame.error:
            self.available = False

    def play_music(self, path, loops=-1):
        """Streams a background WAV file. Loops infinitely at 75% volume."""
        if not self.available:
            return

        try:
            pygame.mixer.music.load(str(path))

            pygame.mixer.music.set_volume(0.0 if self.muted else self.music_volume)

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
            pygame.mixer.music.set_volume(0.0 if self.muted else self.music_volume)
