from kivy.uix.image import Image
from kivy.graphics import PushMatrix, PopMatrix, Rotate
from random import randint

class FallingItem(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = 'assets/images/heart_full.png'
        self.size_hint = (None, None)
        self.size = (100, 100)
        self.x = randint(100, 700)
        self.y = -100 
        self.velocity_y = randint(15, 25) 
        self.gravity = 0.5
        
        if self.x < 400:
            self.velocity_x = randint(2, 5)
        else:
            self.velocity_x = randint(-5, -2)
            
        self.angle = 0
        self.rotation_speed = randint(-5, 5)
        
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