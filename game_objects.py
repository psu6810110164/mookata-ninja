from math import sqrt
from random import randint, choice
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.graphics import PushMatrix, PopMatrix, Rotate

class FallingItem(Image):
    def __init__(self, difficulty=1.0, is_bomb=False, **kwargs):
        super().__init__(**kwargs)
        
        self.is_bomb = is_bomb
        if self.is_bomb:
            self.source = 'assets/bombb.png'
        else:
            self.source = choice(['assets/ood.png', 'assets/vegtb.png', 'assets/meat.png', 'assets/tomato.png' ])
            
        self.size_hint = (None, None)
        base_size = Window.height * 0.15
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

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y -= self.gravity
        self.angle += self.rotation_speed
        self.update_canvas()
