from kivy.uix.image import Image
from kivy.properties import NumericProperty, StringProperty

class FallingItem(Image):
    velocity_y = NumericProperty(0)
    item_type = StringProperty("pork")

    def update(self, dt):
        self.y -= self.velocity_y * dt