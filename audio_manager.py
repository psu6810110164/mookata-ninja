from kivy.core.audio import SoundLoader

class AudioManager:
    def __init__(self):
        self.slash_sound = SoundLoader.load('assets/sounds/slash.wav')
        self.sizzle_sound = SoundLoader.load('assets/sounds/sizzle.wav')
        self.bg_music = SoundLoader.load('assets/sounds/bgm.wav')

    def play_slash(self):
        if self.slash_sound:
            self.slash_sound.play()

    def play_sizzle(self):
        if self.sizzle_sound:
            self.sizzle_sound.play()

    def play_bgm(self):
        if self.bg_music:
            self.bg_music.loop = True
            self.bg_music.play()

    def stop_bgm(self):
        if self.bg_music:
            self.bg_music.stop()