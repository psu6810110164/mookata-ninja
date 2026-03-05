from math import sqrt
from random import randint, choice
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.graphics import PushMatrix, PopMatrix, Rotate

class FallingItem(Image):
    # 👇 เปลี่ยนมารับค่า item_type แทน is_bomb
    def __init__(self, difficulty=1.0, item_type='normal', **kwargs):
        super().__init__(**kwargs)
        
        self.item_type = item_type
        self.is_bomb = (self.item_type == 'bomb')
        
        # 👇 เช็กประเภทเพื่อดึงรูปให้ถูกต้อง
        if self.item_type == 'bomb':
            self.source = 'assets/images/bombb.png'
        elif self.item_type == 'ice':
            self.source = 'assets/images/ice.png'
        elif self.item_type == 'chili':
            self.source = 'assets/images/chili.png'
        else:
            self.source = choice(['assets/images/ood.png', 'assets/images/vegtb.png', 'assets/images/meat.png', 'assets/images/tomato.png'])
            
        self.size_hint = (None, None)
        base_size = Window.height * 0.15
        
        if self.is_bomb:
            self.size = (base_size * 2, base_size * 2)
        else:
            self.size = (base_size, base_size)
            
        screen_w = Window.width
        self.x = randint(int(screen_w * 0.1), int(screen_w * 0.9))
        self.y = -self.height
        
        target_height = Window.height * (randint(60, 85) / 100.0)
        distance_to_travel = target_height - self.y
        
        speed_multiplier = 1.0 + (difficulty * 0.05)
        
        self.gravity = (Window.height * 0.0005) * speed_multiplier
        
        self.velocity_y = sqrt(2 * self.gravity * distance_to_travel)
        
        x_force = Window.width * 0.005 * speed_multiplier
        if self.x < screen_w / 2:
            self.velocity_x = randint(int(x_force * 0.5), int(x_force))
        else:
            self.velocity_x = randint(int(-x_force), int(-x_force * 0.5))
            
        self.angle = 0
        self.rotation_speed = randint(-3, 3) * speed_multiplier
        
        with self.canvas.before:
            PushMatrix()
            self.rot = Rotate()
            self.rot.origin = self.center
            self.rot.angle = self.angle
        with self.canvas.after:
            PopMatrix()
            
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.rot.origin = self.center
        self.rot.angle = self.angle

    # 👇 เพิ่ม time_scale=1.0 เพื่อรองรับระบบ Slow-motion ของน้ำแข็ง
    def update(self, time_scale=1.0):
        self.x += self.velocity_x * time_scale
        self.y += self.velocity_y * time_scale
        self.velocity_y -= self.gravity * time_scale
        self.angle += self.rotation_speed * time_scale
        self.update_canvas()