import math
import time
from random import randint, random
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.core.window import Window
import os
from kivy.graphics import Color, Mesh, Ellipse, Rectangle, PushMatrix, PopMatrix, Rotate
from kivy.clock import Clock
from game_objects import FallingItem
from kivy.animation import Animation
from kivy.uix.image import Image

Window.size = (800, 450)

Builder.load_file('mookata.kv')

class SlicedHalf(Image):
    def __init__(self, orig_texture, is_left, orig_pos, orig_size, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (orig_size[0] / 2, orig_size[1])
        self.allow_stretch = True
        self.keep_ratio = False
        
        tw, th = orig_texture.width, orig_texture.height
        
        with self.canvas.before:
            PushMatrix()
            self.rot = Rotate(angle=0, origin=self.center)
        with self.canvas.after:
            PopMatrix()
            
        if is_left:
            self.texture = orig_texture.get_region(0, 0, tw / 2, th)
            self.pos = (orig_pos[0], orig_pos[1])
            target_x = orig_pos[0] - 80 
            target_rot = 90
        else:
            self.texture = orig_texture.get_region(tw / 2, 0, tw / 2, th)
            self.pos = (orig_pos[0] + (orig_size[0] / 2), orig_pos[1])
            target_x = orig_pos[0] + (orig_size[0] / 2) + 80
            target_rot = -90
            
        target_y = orig_pos[1] - 300 
        self.bind(pos=self.update_rot_origin)
        
        anim_pos = Animation(pos=(target_x, target_y), opacity=0, duration=0.5, t='out_quad')
        anim_rot = Animation(angle=target_rot, duration=0.5, t='out_quad')
        
        anim_pos.bind(on_complete=self.remove_self)
        
        anim_pos.start(self)
        anim_rot.start(self.rot)

    def update_rot_origin(self, *args):
        self.rot.origin = self.center

    def remove_self(self, anim, widget):
        if self.parent:
            self.parent.remove_widget(self)

class MainMenuScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class GameScreen(Screen):
    game_objects = []
    time_elapsed = 0
    score = 0
    combo_count = 0
    last_hit_time = 0

    def on_enter(self):
        self.game_objects = []
        self.time_elapsed = 0
        self.score = 0
        self.combo_count = 0
        self.last_hit_time = 0
        self.temp_hp = 3
        self.ids.combo_shadow.text = ""
        self.ids.combo_main.text = ""
        self.ids.combo_highlight.text = ""
        self.update_lives(self.temp_hp)
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
        if difficulty_level > 1: spawn_count = randint(1, 2)
        if difficulty_level > 3: spawn_count = randint(2, 4)
        if difficulty_level > 5: spawn_count = randint(3, 6)
        for _ in range(spawn_count):
            is_bomb = False
            if difficulty_level > 0.5 and random() < 0.3: is_bomb = True
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
        current_time = time.time()
        for item in self.game_objects[:]:
            if item.collide_point(touch.x, touch.y): 
                if item.is_bomb:
                    if hasattr(self, 'audio'):
                        self.audio.play_bomb()
                    self.test_damage() 
                    self.combo_count = 0
                    self.ids.combo_shadow.text = ""
                    self.ids.combo_main.text = ""
                    self.ids.combo_highlight.text = ""
                    self.create_bomb_effect(touch.x, touch.y)
                    self.remove_widget(item)
                    self.game_objects.remove(item)
                else:
                    if current_time - self.last_hit_time < 1.0: self.combo_count += 1
                    else: self.combo_count = 1
                    self.last_hit_time = current_time
                    self.score += 10 * self.combo_count
                    if self.combo_count > 1: self.show_combo_text(touch.x, touch.y)
                    self.create_slice_effect(item)
                    self.create_hit_effect(touch.x, touch.y)
                    self.remove_widget(item)
                    self.game_objects.remove(item)

    def create_slice_effect(self, item):
        if not item.texture: return
        left_half = SlicedHalf(item.texture, True, item.pos, item.size)
        right_half = SlicedHalf(item.texture, False, item.pos, item.size)
        self.add_widget(left_half)
        self.add_widget(right_half)

    def create_bomb_effect(self, x, y):
        with self.canvas.after:
            flash_color = Color(1, 0, 0, 0.6)
            flash_rect = Rectangle(pos=(0, 0), size=Window.size)
            wave1_color = Color(1, 0.4, 0, 0.9)
            wave1 = Ellipse(pos=(x-20, y-20), size=(40, 40))
            wave2_color = Color(1, 0.8, 0, 0.9)
            wave2 = Ellipse(pos=(x-10, y-10), size=(20, 20))

        anim_flash = Animation(a=0, duration=0.3)
        anim_w1 = Animation(size=(500, 500), pos=(x-250, y-250), duration=0.4, t='out_quad')
        anim_c1 = Animation(a=0, duration=0.4)
        anim_w2 = Animation(size=(300, 300), pos=(x-150, y-150), duration=0.3, t='out_quad')
        anim_c2 = Animation(a=0, duration=0.3)

        def remove_effect(anim, widget):
            self.canvas.after.remove(flash_color)
            self.canvas.after.remove(flash_rect)
            self.canvas.after.remove(wave1_color)
            self.canvas.after.remove(wave1)
            self.canvas.after.remove(wave2_color)
            self.canvas.after.remove(wave2)

        anim_w1.bind(on_complete=remove_effect)
        anim_flash.start(flash_color)
        anim_w1.start(wave1)
        anim_c1.start(wave1_color)
        anim_w2.start(wave2)
        anim_c2.start(wave2_color)

    def create_hit_effect(self, x, y):
        with self.canvas.after:
            color = Color(1, 1, 0.8, 1)
            ellipse = Ellipse(pos=(x-20, y-20), size=(40, 40))
        
        anim_size = Animation(size=(100, 100), pos=(x-50, y-50), duration=0.2)
        anim_alpha = Animation(a=0, duration=0.2)
        
        def remove_effect(anim, widget):
            self.canvas.after.remove(color)
            self.canvas.after.remove(ellipse)
            
        anim_size.bind(on_complete=remove_effect)
        anim_size.start(ellipse)
        anim_alpha.start(color)

    def show_combo_text(self, item_x, item_y):
        txt = f"{self.combo_count}x\nCOMBO!"
        scale_factor = Window.height / 450.0
        normal_size = 45 * scale_factor
        pop_size = 65 * scale_factor
        margin = 80
        safe_x = max(margin, min(item_x, Window.width - margin))
        safe_y = max(margin, min(item_y + 80, Window.height - margin))
        for lbl_id in ['combo_shadow', 'combo_main', 'combo_highlight']:
            lbl = self.ids[lbl_id]
            lbl.text = txt
            lbl.font_size = normal_size
            lbl.center_x = safe_x
            lbl.center_y = safe_y
            if lbl_id == 'combo_shadow': lbl.center_y -= 2
            if lbl_id == 'combo_highlight': lbl.center_y += 2
        anim = Animation(font_size=pop_size, duration=0.1, t='out_back') + \
               Animation(font_size=normal_size, duration=0.1)
        anim.start(self.ids.combo_shadow)
        anim.start(self.ids.combo_main)
        anim.start(self.ids.combo_highlight)
        Clock.unschedule(self.hide_combo_text)
        Clock.schedule_once(self.hide_combo_text, 1.5)

    def hide_combo_text(self, dt):
        for lbl_id in ['combo_shadow', 'combo_main', 'combo_highlight']:
            lbl = self.ids[lbl_id]
            lbl.text = ""
            lbl.color = (0, 0, 0, 0)

    def on_touch_down(self, touch):
        touch.ud['trail'] = [(touch.x, touch.y)]
        self.check_collision(touch)
        with self.canvas:
            touch.ud['color_glow'] = Color(1, 0.4, 0, 0.4)
            touch.ud['mesh_glow'] = Mesh(mode='triangle_strip')
            touch.ud['color_core'] = Color(1, 0.9, 0.2, 1)
            touch.ud['mesh_core'] = Mesh(mode='triangle_strip')
        touch.ud['decay_event'] = Clock.schedule_interval(lambda dt: self.decay_trail(touch), 0.02)
        return super().on_touch_down(touch)

    def decay_trail(self, touch):
        if 'trail' not in touch.ud or len(touch.ud['trail']) <= 2: return
        touch.ud['trail'].pop(0)
        self.update_slash(touch)

    def on_touch_move(self, touch):
        self.check_collision(touch)
        if 'trail' not in touch.ud: return super().on_touch_move(touch)
        last_x, last_y = touch.ud['trail'][-1]
        if math.hypot(touch.x - last_x, touch.y - last_y) > 10:
            touch.ud['trail'].append((touch.x, touch.y))
            if len(touch.ud['trail']) > 12: touch.ud['trail'].pop(0)
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
            thick_glow, thick_core = curve * 25, curve * 8
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
        if 'decay_event' in touch.ud: touch.ud['decay_event'].cancel()
        if 'mesh_glow' in touch.ud:
            self.canvas.remove(touch.ud['color_glow'])
            self.canvas.remove(touch.ud['mesh_glow'])
            self.canvas.remove(touch.ud['color_core'])
            self.canvas.remove(touch.ud['mesh_core'])
        return super().on_touch_up(touch)

    def update_lives(self, current_lives):
        for i in range(1, 4):
            getattr(self.ids, f'life_{i}').source = f'assets/images/heart_{"full" if current_lives >= i else "empty"}.png'

    def test_damage(self):
        if not hasattr(self, 'temp_hp'): self.temp_hp = 3
        self.temp_hp -= 1
        self.update_lives(self.temp_hp)
        if self.temp_hp <= 0:
            game_over_screen = self.manager.get_screen('gameover')
            if hasattr(game_over_screen.ids, 'score_label'): game_over_screen.ids.score_label.text = f"Your Score: {self.score}"
            game_over_screen.final_score = self.score 
            self.manager.current = "gameover"

class GameOverScreen(Screen):
    final_score = 0 
    def on_enter(self): self.load_highscore()
    def load_highscore(self):
        if os.path.exists("highscore.txt"):
            with open("highscore.txt", "r", encoding="utf-8") as f:
                data = f.read()
                if data: self.ids.highscore_label.text = f"High Score:\n{data}"
    def save_score(self):
        name = self.ids.player_name.text if self.ids.player_name.text.strip() else "Unknown Ninja"
        with open("highscore.txt", "a", encoding="utf-8") as f: f.write(f"{name}: {self.final_score}\n")
        self.ids.player_name.text = "" 
        self.load_highscore()
    def restart_game(self): self.manager.current = "game"

class WindowManager(ScreenManager): pass
class MookataNinjaApp(App):
    def build(self): return WindowManager()

if __name__ == '__main__': MookataNinjaApp().run()