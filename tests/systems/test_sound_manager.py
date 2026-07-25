import pygame

from turing_game.systems.sound_manager import SoundManager


def test_init_defaults():
    manager = SoundManager()
    assert manager.muted is False
    assert manager.music_volume == 0.75


def test_init_mixer_failure_sets_unavailable(monkeypatch):
    def boom():
        raise pygame.error("no audio device")
    monkeypatch.setattr(pygame.mixer, "init", boom)

    manager = SoundManager()
    assert manager.available is False


def test_toggle_mute_flips_state_and_volume(monkeypatch):
    volumes = []
    monkeypatch.setattr(pygame.mixer.music, "set_volume", volumes.append)

    manager = SoundManager()
    manager.available = True  # force the volume branch regardless of real device
    manager.muted = False

    manager.toggle_mute()
    assert manager.muted is True
    assert volumes[-1] == 0.0  # muted -> silent

    manager.toggle_mute()
    assert manager.muted is False
    assert volumes[-1] == manager.music_volume  # unmuted -> restored


def test_play_music_noop_when_unavailable(monkeypatch):
    loaded = []
    monkeypatch.setattr(pygame.mixer.music, "load", loaded.append)

    manager = SoundManager()
    manager.available = False
    manager.play_music("track.wav")

    assert loaded == []  # bailed out before touching the mixer


def test_play_music_handles_load_error(monkeypatch, capsys):
    def boom(_path):
        raise pygame.error("bad file")
    monkeypatch.setattr(pygame.mixer.music, "load", boom)

    manager = SoundManager()
    manager.available = True
    manager.play_music("missing.wav")  # should swallow the error

    assert "Could not load music track" in capsys.readouterr().out


def test_stop_music_calls_mixer_when_available(monkeypatch):
    stopped = []
    monkeypatch.setattr(pygame.mixer.music, "stop", lambda: stopped.append(True))

    manager = SoundManager()
    manager.available = True
    manager.stop_music()

    assert stopped == [True]
