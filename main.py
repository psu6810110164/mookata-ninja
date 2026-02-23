from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.core.window import Window

Window.size = (800, 450)

Builder.load_file('mookata.kv')

class MainMenuScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class GameScreen(Screen):
    def on_touch_down(self, touch):
        print(f"เริ่มแตะที่พิกัด: {touch.pos}")
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        print(f"ลากนิ้วไปที่: {touch.pos}")
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        print("ปล่อยนิ้วแล้ว")
        return super().on_touch_up(touch)

class GameOverScreen(Screen):
    pass

class WindowManager(ScreenManager):
    pass

class MookataNinjaApp(App):
    def build(self):
        return WindowManager()

if __name__ == '__main__':
    MookataNinjaApp().run()