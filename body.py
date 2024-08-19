from AABB import AABB
from matter import Matter
from shape import ShapeType, Box, Circle
from transform import Transform
from vector import Vector2


class Body:
    position: Vector2
    linear_velocity: Vector2
    angle: float
    angular_velocity: float
    force: Vector2

    shape: Box | Circle
    matter: Matter
    is_static: bool

    mass: float
    inv_mass: float
    inertia: float
    inv_inertia: float

    transform_update_required: bool
    aabb_update_required: bool

    def __init__(self, shape, matter, x, y, angle=0, is_static=False):

        self.position = Vector2(x, y)
        self.linear_velocity = Vector2()
        self.angle = angle
        self.angular_velocity = 0
        self.force = Vector2()

        self.shape = shape
        self.matter = matter
        self.is_static = is_static
        self.mass = 0
        self.inv_mass = 0
        self.inertia = 0
        self.inv_inertia = 0

        if self.shape.type is ShapeType.BOX:
            self.vertices = self.create_box_vertices(self.shape.width, self.shape.height)
            self.transformed_vertices = self.vertices
        else:
            self.vertices = None
            self.transformed_vertices = None

        self.AABB = None

        self.transform_update_required = True
        self.aabb_update_required = True

        self.init()

    def init(self):
        self.matter.density = 0 if self.is_static else self.matter.density

        self.mass = self.shape.area * self.matter.density
        self.inv_mass = 1 / self.mass if self.mass != 0 else 0

        if self.shape.type is ShapeType.BOX:
            self.inertia = (1.0 / 12.0) * self.mass * (self.shape.width ** 2 + self.shape.height ** 2)
        elif self.shape.type is ShapeType.CIRCLE:
            self.inertia = (1.0 / 2.0) * self.mass * self.shape.radius ** 2
        else:
            raise ValueError("Invalid shape type")
        self.inv_inertia = 1 / self.inertia if self.inertia != 0 else 0

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

    def get_AABB(self):
        if self.aabb_update_required:
            min_x, min_y = float('inf'), float('inf')
            max_x, max_y = float('-inf'), float('-inf')

            if self.shape.type is ShapeType.BOX:
                vertices = self.get_transformed_vertices()

                for v in vertices:
                    min_x = min(min_x, v.x)
                    min_y = min(min_y, v.y)
                    max_x = max(max_x, v.x)
                    max_y = max(max_y, v.y)

            elif self.shape.type is ShapeType.CIRCLE:
                min_x = self.position.x - self.shape.radius
                min_y = self.position.y - self.shape.radius
                max_x = self.position.x + self.shape.radius
                max_y = self.position.y + self.shape.radius

            else:
                raise ValueError("Invalid shape type")

            self.AABB = AABB(min_x, min_y, max_x, max_y)

        self.aabb_update_required = False
        return self.AABB


    def step(self, dt, gravity, iterations):

        if self.is_static:
            return

        dt /= iterations

        # acceleration = self.force / self.mass
        # self.linear_velocity += acceleration * dt

        self.linear_velocity += gravity * dt
        self.position += self.linear_velocity * dt

        self.angle += self.angular_velocity * dt

        self.force.zero()
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

    def rotate_to(self, angle):
        self.angle = angle
        self.transform_update_required = True
        self.aabb_update_required = True

    def apply_force(self, force: Vector2):
        self.force += force
