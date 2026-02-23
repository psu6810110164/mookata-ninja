from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.core.window import Window
import os

Window.size = (800, 450)

Builder.load_file('mookata.kv')

class MainMenuScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class GameScreen(Screen):
    pass

class GameOverScreen(Screen):
    def on_enter(self):
        self.load_highscore()

    def load_highscore(self):
        if os.path.exists("highscore.txt"):
            with open("highscore.txt", "r", encoding="utf-8") as f:
                data = f.read()
                if data:
                    self.ids.highscore_label.text = f"High Score:\n{data}"
        else:
            self.ids.highscore_label.text = "High Score: No data yet"

    def save_score(self):
        name = self.ids.player_name.text
        if not name.strip():
            name = "Unknown Ninja"
            
        current_score = 0 
        
        with open("highscore.txt", "a", encoding="utf-8") as f:
            f.write(f"{name}: {current_score}\n")
            
        self.ids.player_name.text = ""  
        self.load_highscore()
    def restart_game(self):
        self.manager.current = "game"

class WindowManager(ScreenManager):
    pass

class MookataNinjaApp(App):
    def build(self):
        return WindowManager()

if __name__ == '__main__':
    MookataNinjaApp().run()