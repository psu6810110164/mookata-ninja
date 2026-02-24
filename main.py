import math
from random import randint, random
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.core.window import Window
import os

Window.size = (800, 450)
from kivy.graphics import Color, Mesh
from kivy.clock import Clock
from game_objects import FallingItem

Builder.load_file('mookata.kv')

class MainMenuScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class GameScreen(Screen):
    game_objects = []
    time_elapsed = 0
    score = 0

    def on_enter(self):
        self.game_objects = []
        self.time_elapsed = 0
        self.score = 0
        Clock.schedule_interval(self.game_loop, 1.0/60.0)
        self.spawn_next_item(0)

    def on_leave(self):
        Clock.unschedule(self.game_loop)
        Clock.unschedule(self.spawn_next_item)
        for obj in self.game_objects:
            self.remove_widget(obj)
        self.game_objects.clear()

    def spawn_next_item(self, dt):
        difficulty_level = self.time_elapsed / 10.0
        
        spawn_count = 1
        if difficulty_level > 1:
            spawn_count = randint(1, 2)
        if difficulty_level > 3:
            spawn_count = randint(2, 4)
        if difficulty_level > 5:
            spawn_count = randint(3, 6)
            
        for _ in range(spawn_count):
            is_bomb = False
            if difficulty_level > 0.5 and random() < 0.3:
                is_bomb = True
            
            item = FallingItem(difficulty=difficulty_level, is_bomb=is_bomb)
            self.add_widget(item)
            self.game_objects.append(item)
        
        base_delay = max(0.8, 2.5 - (self.time_elapsed * 0.05))
        next_spawn_delay = base_delay + (randint(-3, 3) * 0.1)
        Clock.schedule_once(self.spawn_next_item, next_spawn_delay)

    def game_loop(self, dt):
        self.time_elapsed += dt
        for item in self.game_objects[:]:
            item.update()
            if item.y < -item.height * 2:
                self.remove_widget(item)
                self.game_objects.remove(item)

    def check_collision(self, touch):
        for item in self.game_objects[:]:
            if item.collide_point(touch.x, touch.y): 
                if item.is_bomb:
                    self.test_damage() 
                    self.remove_widget(item)
                    self.game_objects.remove(item)
                else:
                    self.score += 10
                    print(f"Score: {self.score}")
                    self.remove_widget(item)
                    self.game_objects.remove(item)

    def on_touch_down(self, touch):
        touch.ud['trail'] = [(touch.x, touch.y)]
        self.check_collision(touch)
        with self.canvas:
            touch.ud['color_glow'] = Color(1, 0.4, 0, 0.4)
            touch.ud['mesh_glow'] = Mesh(mode='triangle_strip')
            touch.ud['color_core'] = Color(1, 0.9, 0.2, 1)
            touch.ud['mesh_core'] = Mesh(mode='triangle_strip')
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        self.check_collision(touch)
        if 'trail' not in touch.ud: return super().on_touch_move(touch)
        last_x, last_y = touch.ud['trail'][-1]
        if math.hypot(touch.x - last_x, touch.y - last_y) > 15:
            touch.ud['trail'].append((touch.x, touch.y))
            if len(touch.ud['trail']) > 15: touch.ud['trail'].pop(0)
            self.update_slash(touch)
        return super().on_touch_move(touch)

    def update_slash(self, touch):
        trail = touch.ud['trail']
        if len(trail) < 2: return
        v_glow, v_core, indices = [], [], []
        for i in range(len(trail)):
            x, y = trail[i]
            progress = i / (len(trail) - 1)
            curve = math.sin((progress ** 2) * math.pi)
            thick_glow = (curve * 18) + (4 * (1 - progress))
            thick_core = (curve * 5) + (1.5 * (1 - progress))
            if i < len(trail) - 1: dx, dy = trail[i+1][0] - x, trail[i+1][1] - y
            else: dx, dy = x - trail[i-1][0], y - trail[i-1][1]
            length = math.hypot(dx, dy)
            px, py = (-dy/length, dx/length) if length else (0,0)
            v_glow.extend([x+px*thick_glow, y+py*thick_glow, 0, 0, x-px*thick_glow, y-py*thick_glow, 0, 0])
            v_core.extend([x+px*thick_core, y+py*thick_core, 0, 0, x-px*thick_core, y-py*thick_core, 0, 0])
            indices.extend([i*2, i*2+1])
        touch.ud['mesh_glow'].vertices = v_glow
        touch.ud['mesh_glow'].indices = indices
        touch.ud['mesh_core'].vertices = v_core
        touch.ud['mesh_core'].indices = indices

    def on_touch_up(self, touch):
        if 'mesh_glow' in touch.ud:
            self.canvas.remove(touch.ud['color_glow'])
            self.canvas.remove(touch.ud['mesh_glow'])
            self.canvas.remove(touch.ud['color_core'])
            self.canvas.remove(touch.ud['mesh_core'])
        return super().on_touch_up(touch)

    def update_lives(self, current_lives):
        if current_lives >= 1:
            self.ids.life_1.source = 'assets/images/heart_full.png'
        else:
            self.ids.life_1.source = 'assets/images/heart_empty.png'
        if current_lives >= 2:
            self.ids.life_2.source = 'assets/images/heart_full.png'
        else:
            self.ids.life_2.source = 'assets/images/heart_empty.png'
        if current_lives >= 3:
            self.ids.life_3.source = 'assets/images/heart_full.png'
        else:
            self.ids.life_3.source = 'assets/images/heart_empty.png'

    def test_damage(self):
        if not hasattr(self, 'temp_hp'):
            self.temp_hp = 3
        self.temp_hp -= 1
        print(f"HP Left: {self.temp_hp}")
        self.update_lives(self.temp_hp)
        if self.temp_hp <= 0:
            print("Game Over")
            self.temp_hp = 3
            self.update_lives(3)

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