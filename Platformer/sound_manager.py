import pygame
import math
import struct


class SoundManager:
    """Zarządca i generator syntetycznych efektów dźwiękowych dla gniazda i menu (bez dodatkowych zależności)."""

    def __init__(self):
        self.enabled = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.enabled = True
            self.sounds = {
                "click": self._generate_tone(frequency=600, duration=0.06, wave_type="sine"),
                "step": self._generate_tone(frequency=180, duration=0.05, wave_type="sine"),
                "select": self._generate_chime(notes=[523, 659, 784], duration=0.15),
                "mirror": self._generate_chime(notes=[440, 554, 659, 880], duration=0.25),
                "eat": self._generate_tone(frequency=800, duration=0.08, wave_type="square"),
                "sleep": self._generate_chime(notes=[330, 261], duration=0.35),
            }
        except Exception as e:
            print(f"[SoundManager] Synthesizer notification: Mixer disabled or unavailable ({e})")
            self.sounds = {}

    def _generate_tone(self, frequency=440, duration=0.1, wave_type="sine"):
        if not self.enabled:
            return None
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        raw_bytes = bytearray()

        for i in range(n_samples):
            t = i / sample_rate
            if wave_type == "square":
                val = 1.0 if math.sin(2 * math.pi * frequency * t) >= 0 else -1.0
            else:
                val = math.sin(2 * math.pi * frequency * t)

            envelope = math.exp(-3 * t / duration)
            sample_val = int(val * envelope * 0.3 * 32767)
            sample_val = max(-32768, min(32767, sample_val))
            # Stereo 16-bit signed little-endian
            raw_bytes.extend(struct.pack("<hh", sample_val, sample_val))

        return pygame.mixer.Sound(buffer=bytes(raw_bytes))

    def _generate_chime(self, notes=[440, 554, 659], duration=0.2):
        if not self.enabled:
            return None
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        raw_bytes = bytearray()

        note_dur = duration / len(notes)
        for i in range(n_samples):
            t = i / sample_rate
            val = 0.0
            for idx, freq in enumerate(notes):
                start_t = idx * note_dur
                if t >= start_t:
                    sub_t = t - start_t
                    val += math.sin(2 * math.pi * freq * sub_t) * math.exp(-4 * sub_t)

            val = (val / len(notes)) * 0.3
            sample_val = int(val * 32767)
            sample_val = max(-32768, min(32767, sample_val))
            raw_bytes.extend(struct.pack("<hh", sample_val, sample_val))

        return pygame.mixer.Sound(buffer=bytes(raw_bytes))

    def play(self, sound_name):
        if self.enabled and sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except Exception:
                pass

