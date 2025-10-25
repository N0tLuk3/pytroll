# sound_player.py
import base64
import io
import pygame
import threading
import time
import config


def play_sound_from_base64(b64_data):
    """Dekodiert Base64-Daten und spielt sie mit pygame ab."""
    try:
        # Base64 → Bytes
        sound_bytes = base64.b64decode(b64_data)

        # Pygame Mixer initialisieren (nur einmal)
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2)

        # Bytes in einen Buffer packen
        sound_file = io.BytesIO(sound_bytes)

        # Sound laden und abspielen
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()

        print("🔊 Sound abgespielt.")
    except Exception as e:
        print(f"Fehler beim Abspielen des Sounds: {e}")


def schedule_test_sound(interval_minutes: int = 10):
    """
    Startet einen Thread, der alle X Minuten den Sound aus config.SOUND_B64 abspielt.
    Default: alle 10 Minuten.
    """
    def sound_loop():
        while True:
            play_sound_from_base64(config.SOUND_B64)
            time.sleep(interval_minutes * 60)

    threading.Thread(target=sound_loop, daemon=True).start()
