from typing import Union, List
from collisions import Collisions
from vector import Vector2


class World:
    MIN_ITERATIONS = 1
    MAX_ITERATIONS = 16

    def __init__(self, gravity: Vector2 = Vector2(0, 0)):
        self.bodies = []
        self.gravity = gravity

    def add_body(self, body: Union[List[object], object]):
        if isinstance(body, list):
            self.bodies.extend(body)
        else:
            self.bodies.append(body)

    def remove_body(self, body: Union[List[object], object]):
        if isinstance(body, list):
            for b in body:
                self.bodies.remove(b)
        else:
            self.bodies.remove(body)

    def clear(self):
        self.bodies.clear()

    def get_body(self, index: int) -> object:
        if index < 0 or index >= len(self.bodies):
            raise IndexError("Body index out of range.")
        return self.bodies[index]

    def step(self, dt, iterations: int = 1):

        iterations = max(min(iterations, self.MAX_ITERATIONS), self.MIN_ITERATIONS)

        for _ in range(iterations):
            for body in self.bodies:
                body.step(dt, self.gravity, iterations)

        for i in range(len(self.bodies) - 1):
            bodyA = self.bodies[i]

            for j in range(i + 1, len(self.bodies)):
                bodyB = self.bodies[j]

                if self.bodies[i].is_static and self.bodies[j].is_static:
                    continue

                collision, normal, depth = Collisions.Collide(bodyA, bodyB)

                if collision:

                    if bodyA.is_static:
                        bodyB.move(normal * depth)

                    elif bodyB.is_static:
                        bodyA.move(-normal * depth)

                    else:
                        bodyA.move(-normal * depth / 2)
                        bodyB.move(normal * depth / 2)