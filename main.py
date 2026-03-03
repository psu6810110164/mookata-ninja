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

import random as rnd

try:
    from audio_manager import AudioManager
except ImportError:
    pass

Window.size = (800, 450)

Builder.load_file('mookata.kv')

class SlicedHalf(Image):
    def __init__(self, orig_texture, is_left, orig_center, orig_size, slash_angle, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (orig_size[0] / 2, orig_size[1])
        self.allow_stretch = True
        self.keep_ratio = False
        
        tw, th = orig_texture.width, orig_texture.height
        if is_left:
            self.texture = orig_texture.get_region(0, 0, tw / 2, th)
        else:
            self.texture = orig_texture.get_region(tw / 2, 0, tw / 2, th)
            
        alpha = slash_angle - 90
        rad = math.radians(alpha)
        w, h = orig_size
        dir_sign = -1 if is_left else 1
        
        local_x = dir_sign * w / 4
        start_cx = orig_center[0] + local_x * math.cos(rad)
        start_cy = orig_center[1] + local_x * math.sin(rad)
        self.pos = (start_cx - self.size[0] / 2, start_cy - self.size[1] / 2)
        
        with self.canvas.before:
            PushMatrix()
            self.rot = Rotate(angle=alpha, origin=self.center)
        with self.canvas.after:
            PopMatrix()
            
        self.bind(pos=self.update_rot_origin)
        
        peak_local_x = local_x + (dir_sign * 30)
        peak_cx = orig_center[0] + peak_local_x * math.cos(rad)
        peak_cy = orig_center[1] + peak_local_x * math.sin(rad) + 50
        peak_pos = (peak_cx - self.size[0] / 2, peak_cy - self.size[1] / 2)
        
        target_local_x = local_x + (dir_sign * 100)
        target_cx = orig_center[0] + target_local_x * math.cos(rad)
        target_cy = orig_center[1] + target_local_x * math.sin(rad) - 400
        target_pos = (target_cx - self.size[0] / 2, target_cy - self.size[1] / 2)
        
        target_rot = alpha + (dir_sign * 120)
        
        anim_pos = Animation(pos=peak_pos, duration=0.3, t='out_quad') + \
                   Animation(pos=target_pos, opacity=0, duration=1.2, t='in_quad')
        anim_rot = Animation(angle=target_rot, duration=1.5, t='linear')
        
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
    is_paused = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.audio = AudioManager()

    def on_enter(self):
        self.game_objects = []
        self.time_elapsed = 0
        self.score = 0
        self.is_paused = False
        if 'current_score_label' in self.ids:
            self.ids.current_score_label.text = f"Score: {self.score}"
        self.combo_count = 0
        self.last_hit_time = 0
        self.temp_hp = 3
        self.ids.combo_shadow.text = ""
        self.ids.combo_main.text = ""
        self.ids.combo_highlight.text = ""
        self.update_lives(self.temp_hp)
        
        if 'pause_overlay' in self.ids:
            self.ids.pause_overlay.opacity = 0
            self.ids.pause_overlay.disabled = True
            
        if hasattr(self, 'audio') and hasattr(self.audio, 'play_bgm'):
            self.audio.play_bgm()
        Clock.schedule_interval(self.game_loop, 1.0/60.0)
        self.spawn_next_item(0)

    def on_leave(self):
        if hasattr(self, 'audio') and hasattr(self.audio, 'stop_bgm'):
            self.audio.stop_bgm()
        Clock.unschedule(self.game_loop)
        Clock.unschedule(self.spawn_next_item)
        for obj in self.game_objects:
            self.remove_widget(obj)
        self.game_objects.clear()

    def pause_game(self):
        self.is_paused = True
        if 'pause_overlay' in self.ids:
            overlay = self.ids.pause_overlay
            
            if overlay.parent:
                overlay.parent.remove_widget(overlay)
                self.add_widget(overlay)
                
            overlay.opacity = 1
            overlay.disabled = False

    def resume_game(self):
        self.is_paused = False
        if 'pause_overlay' in self.ids:
            self.ids.pause_overlay.opacity = 0
            self.ids.pause_overlay.disabled = True

    def quit_game(self):
        self.resume_game()
        game_over_screen = self.manager.get_screen('gameover')
        if hasattr(game_over_screen.ids, 'score_label'): 
            game_over_screen.ids.score_label.text = f"Your Score: {self.score}"
        game_over_screen.final_score = self.score 
        self.manager.current = "gameover"

    def spawn_next_item(self, dt):
        if self.is_paused:
            Clock.schedule_once(self.spawn_next_item, 0.1)
            return
            
        difficulty_level = self.time_elapsed / 10.0
        spawn_count = 1
        if difficulty_level > 1: spawn_count = randint(1, 2)
        if difficulty_level > 3: spawn_count = randint(2, 4)
        if difficulty_level > 5: spawn_count = randint(3, 6)
        for _ in range(spawn_count):
            is_bomb = False
            if difficulty_level > 0.5 and random() < 0.15: is_bomb = True
            item = FallingItem(difficulty=difficulty_level, is_bomb=is_bomb)
            
            insert_idx = len(self.children) - 1 if len(self.children) > 0 else 0
            self.add_widget(item, index=insert_idx)
            
            self.game_objects.append(item)
        base_delay = max(0.8, 2.5 - (self.time_elapsed * 0.05))
        next_spawn_delay = base_delay + (randint(-3, 3) * 0.1)
        Clock.schedule_once(self.spawn_next_item, next_spawn_delay)

    def game_loop(self, dt):
        if self.is_paused:
            return
            
        self.time_elapsed += dt
        for item in self.game_objects[:]:
            item.update()
            if item.y < -item.height * 2:
                self.remove_widget(item)
                self.game_objects.remove(item)

    def check_collision(self, touch):
        current_time = time.time()
        
        trail = touch.ud.get('trail', [])
        if len(trail) >= 2:
            dx = trail[-1][0] - trail[0][0]
            dy = trail[-1][1] - trail[0][1]
        else:
            dx = touch.dx
            dy = touch.dy
            
        if dx == 0 and dy == 0:
            slash_angle = 90
        else:
            slash_angle = math.degrees(math.atan2(dy, dx))

        for item in self.game_objects[:]:
            if item.collide_point(touch.x, touch.y): 
                if item.is_bomb:
                    if hasattr(self, 'audio') and hasattr(self.audio, 'play_bomb'):
                        self.audio.play_bomb()
                    self.test_damage() 
                    self.combo_count = 0
                    self.ids.combo_shadow.text = ""
                    self.ids.combo_main.text = ""
                    self.ids.combo_highlight.text = ""
                    self.create_bomb_effect(touch.x, touch.y)
                    self.trigger_screenshake()
                    self.remove_widget(item)
                    self.game_objects.remove(item)
                else:
                    if hasattr(self, 'audio') and hasattr(self.audio, 'play_slash'):
                        self.audio.play_slash()
                    if current_time - self.last_hit_time < 1.0: self.combo_count += 1
                    else: self.combo_count = 1
                    self.last_hit_time = current_time
                    self.score += 10 * self.combo_count

                    self.ids.current_score_label.text = f"Score: {self.score}"

                    if self.combo_count > 1: self.show_combo_text(touch.x, touch.y)
                    self.create_slice_effect(item, slash_angle)
                    self.create_hit_effect(touch.x, touch.y)
                    self.remove_widget(item)
                    self.game_objects.remove(item)

    def create_slice_effect(self, item, slash_angle):
        if not item.texture: return
        orig_center = item.center
        half_1 = SlicedHalf(item.texture, True, orig_center, item.size, slash_angle)
        half_2 = SlicedHalf(item.texture, False, orig_center, item.size, slash_angle)
        
        insert_idx = len(self.children) - 1 if len(self.children) > 0 else 0
        self.add_widget(half_1, index=insert_idx)
        self.add_widget(half_2, index=insert_idx)

    def create_bomb_effect(self, x, y):
        with self.canvas.after:
            flash_color = Color(1, 0, 0, 0.6)
            flash_rect = Rectangle(pos=(0, 0), size=Window.size)

        anim_flash = Animation(a=0, duration=0.3)
        anim_flash.start(flash_color)

        img_size = 50
        explosion = Image(
            source='assets/images/explosion_effect.png', 
            size_hint=(None, None),
            size=(img_size, img_size),
            pos=(x - img_size/2, y - img_size/2)
        )
        
        insert_idx = len(self.children) - 1 if len(self.children) > 0 else 0
        self.add_widget(explosion, index=insert_idx)

        target_size = 350
        anim_exp = Animation(
            size=(target_size, target_size),
            pos=(x - target_size/2, y - target_size/2),
            duration=0.3,
            t='out_quad'
        ) + Animation(opacity=0, duration=0.2)

        def remove_effect(anim, widget):
            if explosion in self.children:
                self.remove_widget(explosion)
            self.canvas.after.remove(flash_color)
            self.canvas.after.remove(flash_rect)

        anim_exp.bind(on_complete=remove_effect)
        anim_exp.start(explosion)

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
        margin = 100
        safe_x = max(margin, min(item_x, Window.width - margin))
        safe_y = max(margin, min(item_y + 80, Window.height - margin))
        normal_size = 60
        pop_size = 90
        
        self.ids.combo_shadow.text = txt
        self.ids.combo_shadow.center_x = safe_x
        self.ids.combo_shadow.center_y = safe_y - 2
        self.ids.combo_shadow.color = (0, 0, 0.5, 1)
        self.ids.combo_shadow.font_size = normal_size

        self.ids.combo_main.text = txt
        self.ids.combo_main.center_x = safe_x
        self.ids.combo_main.center_y = safe_y
        self.ids.combo_main.color = (0, 0.6, 1, 1)
        self.ids.combo_main.font_size = normal_size

        self.ids.combo_highlight.text = txt
        self.ids.combo_highlight.center_x = safe_x
        self.ids.combo_highlight.center_y = safe_y + 2
        self.ids.combo_highlight.color = (0.8, 1, 1, 1)
        self.ids.combo_highlight.font_size = normal_size
        
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
        if self.is_paused:
            return super().on_touch_down(touch)
            
        if hasattr(self, 'audio') and hasattr(self.audio, 'play_slash'):
            self.audio.play_slash()
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
        if self.is_paused:
            return super().on_touch_move(touch)
            
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
        if self.is_paused:
            return super().on_touch_up(touch)
            
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
            if hasattr(game_over_screen.ids, 'score_label'): 
                game_over_screen.ids.score_label.text = f"Your Score: {self.score}"
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