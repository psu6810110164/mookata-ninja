from kivy.core.audio import SoundLoader
import os


class AudioManager:
    def __init__(self):
        # store paths so we can attempt lazy reloads/fallbacks later
        self.slash_path = 'assets/sounds/slash.mp3'
        self.bomb_path = 'assets/sounds/bomb.mp3'
        self.bgm_path = 'assets/sounds/bgm.mp3'

        self.slash_sound = None
        self.sizzle_sound = None
        self.bg_music = None

        # initial load (may return None if no provider/decoder available)
        self._load_all()

    def _safe_load(self, path):
        try:
            s = SoundLoader.load(path)
            print(f"AudioManager: try load '{path}' -> {s}")
            return s
        except Exception as e:
            print(f"AudioManager: exception loading '{path}': {e}")
            return None

    def _load_all(self):
        self.slash_sound = self._safe_load(self.slash_path)
        self.sizzle_sound = self._safe_load(self.bomb_path)
        self.bg_music = self._safe_load(self.bgm_path)
        print("AudioManager: bgm object:", self.bg_music)

    def _try_fallback(self, path):
        # try same filename with .wav extension if exists
        root, _ = os.path.splitext(path)
        wav = root + '.wav'
        if os.path.exists(wav):
            return self._safe_load(wav)
        return None

    def play_slash(self):
        if not self.slash_sound:
            self.slash_sound = self._safe_load(self.slash_path) or self._try_fallback(self.slash_path)
        if self.slash_sound:
            try:
                # ensure audible by default
                self.slash_sound.volume = 1.0
                self.slash_sound.play()
                print('AudioManager: play_slash -> played')
            except Exception as e:
                print('AudioManager: play_slash -> error playing:', e)
        else:
            print('AudioManager: play_slash -> no sound loaded')

    def play_bomb(self):
        if not self.sizzle_sound:
            self.sizzle_sound = self._safe_load(self.bomb_path) or self._try_fallback(self.bomb_path)
        if self.sizzle_sound:
            try:
                self.sizzle_sound.volume = 1.0
                self.sizzle_sound.play()
                print('AudioManager: play_bomb -> played')
            except Exception as e:
                print('AudioManager: play_bomb -> error playing:', e)
        else:
            print('AudioManager: play_bomb -> no sound loaded')

    def play_bgm(self):
        if not self.bg_music:
            self.bg_music = self._safe_load(self.bgm_path) or self._try_fallback(self.bgm_path)
        if self.bg_music:
            try:
                # set sensible defaults
                self.bg_music.loop = True
                # ensure volume set (0-1)
                try:
                    self.bg_music.volume = 0.6
                except Exception:
                    pass
                self.bg_music.play()
                print('AudioManager: play_bgm -> playing')
            except Exception as e:
                print('AudioManager: play_bgm -> error playing:', e)
        else:
            print('AudioManager: play_bgm -> no bgm loaded')

    def stop_bgm(self):
        if self.bg_music:
            try:
                self.bg_music.stop()
                print('AudioManager: stop_bgm -> stopped')
            except Exception as e:
                print('AudioManager: stop_bgm -> error stopping:', e)
        else:
            print('AudioManager: stop_bgm -> no bgm loaded')