import math
from enum import Enum

class ShapeType(Enum):
    CIRCLE = "circle"
    BOX = "box"

class Shape:
    def __init__(self, shape_type: ShapeType):
        self.area = None
        self.type = shape_type

    def get_bounds(self, pos):
        raise NotImplementedError("Subclass must implement abstract method")

class Circle(Shape):
    def __init__(self, radius):
        super().__init__(ShapeType.CIRCLE)
        self.radius = radius
        self.area = math.pi * self.radius ** 2

    def get_bounds(self, pos):
        return pos.x - self.radius, pos.y - self.radius, self.radius * 2, self.radius * 2

class Box(Shape):
    def __init__(self, width, height):
        super().__init__(ShapeType.BOX)
        self.width = width
        self.height = height
        self.area = self.width * self.height

    def get_bounds(self, pos):
        return pos.x - self.width / 2, pos.y - self.height / 2, self.width, self.height
