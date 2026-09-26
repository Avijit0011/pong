import math
import struct
import pygame

class SoundEngine:
    def __init__(self):
        self.enabled = False
        self.muted = False
        self.sounds = {}
        
        try:
            pygame.mixer.init(44100, -16, 1, 512)
            self.enabled = True
            self._generate_sounds()
        except Exception as e:
            print(f"[SoundEngine] Audio init warning: {e}. Running in silent mode.")

    def _create_sine_wave(self, frequency, duration, volume=0.3, pitch_decay=0.0):
        sample_rate = 44100
        num_samples = int(sample_rate * duration)
        buf = bytearray()
        
        for i in range(num_samples):
            t = i / num_samples
            current_freq = max(40.0, frequency * (1.0 - pitch_decay * t))
            angle = 2.0 * math.pi * current_freq * (i / sample_rate)
            
            # Envelope (fade out smoothly at the end)
            env = 1.0 - (t ** 2)
            sample = int(32767 * volume * env * math.sin(angle))
            sample = max(-32768, min(32767, sample))
            buf.extend(struct.pack('<h', sample))
            
        return pygame.mixer.Sound(buffer=bytes(buf))

    def _create_arpeggio(self, freqs, note_duration, volume=0.25):
        sample_rate = 44100
        total_samples = int(sample_rate * note_duration * len(freqs))
        buf = bytearray()
        
        for idx, freq in enumerate(freqs):
            note_samples = int(sample_rate * note_duration)
            for i in range(note_samples):
                t = i / note_samples
                angle = 2.0 * math.pi * freq * (i / sample_rate)
                env = 1.0 - t
                sample = int(32767 * volume * env * math.sin(angle))
                sample = max(-32768, min(32767, sample))
                buf.extend(struct.pack('<h', sample))
                
        return pygame.mixer.Sound(buffer=bytes(buf))

    def _generate_sounds(self):
        if not self.enabled:
            return
            
        try:
            # Paddle hit sound (crisp sine wave beep)
            self.sounds['paddle_hit'] = self._create_sine_wave(587.33, 0.06, volume=0.35) # D5
            
            # Wall hit sound (mid bounce)
            self.sounds['wall_hit'] = self._create_sine_wave(329.63, 0.05, volume=0.25) # E4
            
            # Score goal sound (descending sweep)
            self.sounds['score'] = self._create_sine_wave(440.0, 0.35, volume=0.4, pitch_decay=0.6)
            
            # Power-up collected sound (ascending chime)
            self.sounds['powerup'] = self._create_arpeggio([523.25, 659.25, 783.99, 1046.50], 0.05, volume=0.3)
            
            # Button click sound
            self.sounds['click'] = self._create_sine_wave(880.0, 0.03, volume=0.2)
            
            # Victory sound
            self.sounds['victory'] = self._create_arpeggio([440.0, 554.37, 659.25, 880.0], 0.12, volume=0.35)

            # Power-up spawn notification sound
            self.sounds['powerup_spawn'] = self._create_arpeggio([392.00, 523.25], 0.08, volume=0.25)

            # High rally milestone sound
            self.sounds['rally_milestone'] = self._create_arpeggio([783.99, 1046.50, 1318.51], 0.06, volume=0.35)
        except Exception as e:
            print(f"[SoundEngine] Error generating synth sounds: {e}")

    def play(self, sound_name):
        if not self.enabled or self.muted:
            return
        if sound_name in self.sounds:
            self.sounds[sound_name].play()

    def toggle_mute(self):
        self.muted = not self.muted
        return self.muted
