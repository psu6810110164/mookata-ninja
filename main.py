from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.core.window import Window

Window.size = (800, 450)

Builder.load_file('mookata.kv')

class MainMenuScreen(Screen):
    pass

class GameScreen(Screen):
    pass

class GameOverScreen(Screen):
    pass

class WindowManager(ScreenManager):
    pass

class MookataNinjaApp(App):
    def build(self):
        return WindowManager()

if __name__ == '__main__':
    MookataNinjaApp().run()