import math

from shape import ShapeType
from vector import Vector2


class Transform:
    def __init__(self, x, y, angle):
        self._position_x = x
        self._position_y = y
        self._sin = math.sin(angle)
        self._cos = math.cos(angle)

    @property
    def position_x(self):
        return self._position_x

    @property
    def position_y(self):
        return self._position_y

    @property
    def sin(self):
        return self._sin

    @property
    def cos(self):
        return self._cos

    @staticmethod
    def zero():
        return Transform(0.0, 0.0, 0.0)


class Body:
    def __init__(self, shape, matter, x, y, angle=0, is_static=False):

        self.position = Vector2(x, y)
        self.linear_velocity = Vector2()
        self.angle = angle
        self.angular_velocity = 0

        self.force = Vector2()

        self.shape = shape
        self.is_static = is_static

        self.matter = matter
        self.mass = self.shape.area * self.matter.density
        self.inv_mass = 1 / self.mass if self.mass != 0 else 0

        if self.shape.type is ShapeType.BOX:
            self.vertices = self.create_box_vertices(self.shape.width, self.shape.height)
            self.triangles = self.create_box_triangles()
            self.transformed_vertices = self.vertices
        else:
            self.vertices = None
            self.triangles = None
            self.transformed_vertices = None

        self.transform_update_required = True
        self.aabb_update_required = True

    @staticmethod
    def create_box_vertices(width, height):
        left = -width / 2.0
        right = left + width
        bottom = -height / 2.0
        top = bottom + height

        vertices = [
            Vector2(left, top),
            Vector2(right, top),
            Vector2(right, bottom),
            Vector2(left, bottom)
        ]

        return vertices

    @staticmethod
    def create_box_triangles():
        return [0, 1, 2, 0, 2, 3]

    def get_transformed_vertices(self):
        if self.transform_update_required:
            transform = Transform(self.position.x, self.position.y, self.angle)

            self.transformed_vertices = [Vector2.transform(v, transform) for v in self.vertices]

            self.transform_update_required = False

        return self.transformed_vertices

    def get_vertices(self, tuple=False):
        if tuple:
            return [(v.x, v.y) for v in self.transformed_vertices]
        else:
            return self.transformed_vertices

    def step(self, dt, gravity, iterations):

        if self.is_static:
            return

        dt /= iterations

        # acceleration = self.force / self.mass
        # self.linear_velocity += acceleration * dt

        self.linear_velocity += gravity * dt
        self.position += self.linear_velocity * dt

        self.angle += self.angular_velocity * dt

        self.force = Vector2()
        self.transform_update_required = True
        self.aabb_update_required = True

    def move(self, amount):
        self.position += amount
        self.transform_update_required = True
        self.aabb_update_required = True

    def move_to(self, pos):
        self.position = pos
        self.transform_update_required = True
        self.aabb_update_required = True

    def rotate(self, amount):
        self.angle += amount
        self.transform_update_required = True
        self.aabb_update_required = True

    def apply_force(self, force):
        self.force += force