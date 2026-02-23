import math
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.graphics import Color, Mesh

Window.size = (800, 450)

Builder.load_file('mookata.kv')

class MainMenuScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class GameScreen(Screen):
    def on_touch_down(self, touch):
        touch.ud['trail'] = [(touch.x, touch.y)]
        with self.canvas:
            touch.ud['color_glow'] = Color(1, 0.4, 0, 0.4)
            touch.ud['mesh_glow'] = Mesh(mode='triangle_strip')
            touch.ud['color_core'] = Color(1, 0.9, 0.2, 1)
            touch.ud['mesh_core'] = Mesh(mode='triangle_strip')
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if 'trail' not in touch.ud:
            return super().on_touch_move(touch)
            
        last_x, last_y = touch.ud['trail'][-1]
        if math.hypot(touch.x - last_x, touch.y - last_y) > 15:
            touch.ud['trail'].append((touch.x, touch.y))
            if len(touch.ud['trail']) > 15:
                touch.ud['trail'].pop(0)
            self.update_slash(touch)
        return super().on_touch_move(touch)

    def update_slash(self, touch):
        trail = touch.ud['trail']
        if len(trail) < 2:
            return
            
        v_glow, v_core = [], []
        indices = []
        
        for i in range(len(trail)):
            x, y = trail[i]
            progress = i / (len(trail) - 1)
            
            curve = math.sin((progress ** 2) * math.pi)
            
            thick_glow = (curve * 18) + (4 * (1 - progress))
            thick_core = (curve * 5) + (1.5 * (1 - progress))
            
            if i < len(trail) - 1:
                dx = trail[i+1][0] - x
                dy = trail[i+1][1] - y
            else:
                dx = x - trail[i-1][0]
                dy = y - trail[i-1][1]
                
            length = math.hypot(dx, dy)
            if length == 0:
                px, py = 0, 0
            else:
                px, py = -dy / length, dx / length
            
            v_glow.extend([x + px * thick_glow, y + py * thick_glow, 0, 0, x - px * thick_glow, y - py * thick_glow, 0, 0])
            v_core.extend([x + px * thick_core, y + py * thick_core, 0, 0, x - px * thick_core, y - py * thick_core, 0, 0])
            
            idx = i * 2
            indices.extend([idx, idx+1])
            
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

class GameOverScreen(Screen):
    pass

class WindowManager(ScreenManager):
    pass

class MookataNinjaApp(App):
    def build(self):
        return WindowManager()

if __name__ == '__main__':
    MookataNinjaApp().run()