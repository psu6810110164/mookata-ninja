from kivy.core.audio import SoundLoader

class AudioManager:
    def __init__(self):
        self.slash_sound = SoundLoader.load('assets/sounds/slash.mp3')
        self.sizzle_sound = SoundLoader.load('assets/sounds/bomb.mp3')
        self.bg_music = SoundLoader.load('assets/sounds/bgm.mp3')
        
        # เพิ่มตัวแปรสำหรับจำค่าระดับเสียงปัจจุบัน และสถานะ Mute
        self.current_volume = 0.5 
        self.is_muted = False
        
        # ตั้งค่าระดับเสียงเริ่มต้นให้ทุกไฟล์ตอนเปิดเกม
        self._apply_volume(self.current_volume)

    def play_slash(self):
        # ✅ แก้ไข: เช็กสถานะ Mute ก่อนเล่นเสียง
        if self.slash_sound and not self.is_muted:
            self.slash_sound.volume = self.current_volume
            self.slash_sound.play()

    def play_bomb(self):
        # ✅ แก้ไข: เช็กสถานะ Mute ก่อนเล่นเสียง
        if self.sizzle_sound and not self.is_muted:
            self.sizzle_sound.volume = self.current_volume
            self.sizzle_sound.play()

    def play_bgm(self):
        if self.bg_music:
            self.bg_music.loop = True
            # ✅ แก้ไข: บังคับเซตระดับเสียงอีกรอบก่อนเริ่มเพลง
            self.bg_music.volume = 0 if self.is_muted else self.current_volume
            self.bg_music.play()

    def stop_bgm(self):
        if self.bg_music:
            self.bg_music.stop()

    # ---- 2 ฟังก์ชันสำหรับ Settings เหมือนเดิม ----

    def set_volume(self, volume):
        self.current_volume = volume
        if not self.is_muted:
            self._apply_volume(volume)

    def set_mute(self, is_muted):
        self.is_muted = is_muted
        if self.is_muted:
            self._apply_volume(0)  
        else:
            self._apply_volume(self.current_volume)  

    def _apply_volume(self, volume):
        if self.slash_sound:
            self.slash_sound.volume = volume
        if self.sizzle_sound:
            self.sizzle_sound.volume = volume
        if self.bg_music:
            self.bg_music.volume = volume