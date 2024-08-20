import math
from enum import Enum

from vector import Vector2


class ShapeType(Enum):
    CIRCLE = "circle"
    BOX = "box"
    POLYGON = "polygon"

class Shape:
    def __init__(self, shape_type: ShapeType):
        self.area = None
        self.vertices = None
        self.type = shape_type

class Circle(Shape):
    def __init__(self, radius):
        super().__init__(ShapeType.CIRCLE)
        self.radius = radius
        self.area = self.calculate_area()

    def calculate_area(self):
        return math.pi * self.radius ** 2

class Box(Shape):
    def __init__(self, width, height):
        super().__init__(ShapeType.BOX)
        self.width = width*2
        self.height = height
        self.vertices = self.calculate_vertices(width, height)
        self.area = self.calculate_area()

    def calculate_vertices(self, width, height):
        left = -width / 2.0
        right = left + width
        bottom = -height / 2.0
        top = bottom + height

        return [
            Vector2(left, top),
            Vector2(right, top),
            Vector2(right, bottom),
            Vector2(left, bottom)
        ]

    def calculate_area(self):
        return self.width * self.height

class Polygon(Shape):
    def __init__(self, radius, num_points):
        super().__init__(ShapeType.POLYGON)
        self.radius = radius
        self.num_points = num_points
        self.vertices = self.calculate_vertices()
        self.area = self.calculate_area()

    def calculate_vertices(self):
        vertices = []
        angle_step = 2 * math.pi / self.num_points
        for i in range(self.num_points):
            angle = i * angle_step
            x = self.radius * math.cos(angle)
            y = self.radius * math.sin(angle)
            vertices.append(Vector2(x, y))
        return vertices

    def calculate_area(self):
        return 0.5 * self.num_points * self.radius ** 2 * math.sin(2 * math.pi / self.num_points)