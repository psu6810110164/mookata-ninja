from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.graphics import Color, Line

Window.size = (800, 450)

Builder.load_file('mookata.kv')

class MainMenuScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class GameScreen(Screen):
    def on_touch_down(self, touch):
        with self.canvas:
            Color(1, 0.4, 0, 1) 
            touch.ud['slash_line'] = Line(points=(touch.x, touch.y), width=3)
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if 'slash_line' in touch.ud:
            touch.ud['slash_line'].points += [touch.x, touch.y]
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if 'slash_line' in touch.ud:
            self.canvas.remove(touch.ud['slash_line'])
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