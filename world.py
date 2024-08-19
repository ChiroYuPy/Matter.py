from typing import Union, List
from body import Body
from collisions import Collisions
from manifold import Manifold
from vector import Vector2

class World:
    MIN_ITERATIONS = 1
    MAX_ITERATIONS = 16

    def __init__(self, gravity: Vector2 = Vector2(0, -9.81)):
        self.gravity = gravity
        self.bodies: List[Body] = []
        self.contacts: List[Manifold] = []
        self.contact_points: List[Vector2] = []

    def add_body(self, body: Union[List[Body], Body]):
        if isinstance(body, list):
            if any(not isinstance(b, Body) for b in body):
                raise TypeError("All items in the list must be instances of 'Body'.")
            self.bodies.extend(body)
        else:
            if not isinstance(body, Body):
                raise TypeError("Expected 'Body' instance.")
            self.bodies.append(body)

    def remove_body(self, body: Union[List[Body], Body]):
        if isinstance(body, list):
            for b in body:
                if not isinstance(b, Body):
                    raise TypeError("Expected 'Body' instance.")
                if b in self.bodies:
                    self.bodies.remove(b)
        else:
            if not isinstance(body, Body):
                raise TypeError("Expected 'Body' instance.")
            if body in self.bodies:
                self.bodies.remove(body)

    def clear(self):
        self.bodies.clear()

    def get_body(self, index: int) -> Body:
        if index < 0 or index >= len(self.bodies):
            raise IndexError("Body index out of range.")
        return self.bodies[index]

    def step(self, dt: float, iterations: int = 1):
        iterations = max(min(iterations, self.MAX_ITERATIONS), self.MIN_ITERATIONS)
        self.contact_points.clear()

        for _ in range(iterations):
            for body in self.bodies:
                body.step(dt, self.gravity, iterations)

            self.contacts.clear()

            for i in range(len(self.bodies) - 1):
                bodyA = self.bodies[i]
                bodyA.AABB = bodyA.get_AABB()

                for j in range(i + 1, len(self.bodies)):
                    bodyB = self.bodies[j]
                    bodyB.AABB = bodyB.get_AABB()

                    if bodyA.is_static and bodyB.is_static:
                        continue

                    if not Collisions.IntersectAABB(bodyA.AABB, bodyB.AABB):
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

                        contact1, contact2, contact_count = Collisions.FindContactPoints(bodyA, bodyB)
                        contact = Manifold(bodyA, bodyB, normal, depth, contact1, contact2, contact_count)
                        self.contacts.append(contact)

            for contact in self.contacts:
                self.resolve_collision(contact)

                if contact.contact_count > 0:
                    self.contact_points.append(contact.contact1)
                    if contact.contact_count > 1:
                        self.contact_points.append(contact.contact2)

    @staticmethod
    def resolve_collision(contact: Manifold):
        bodyA = contact.bodyA
        bodyB = contact.bodyB
        normal = contact.normal

        relative_velocity = bodyB.linear_velocity - bodyA.linear_velocity
        print(bodyB.linear_velocity, bodyA.linear_velocity, relative_velocity)

        if relative_velocity.dot(normal) > 0:
            return

        e = min(bodyA.matter.restitution, bodyB.matter.restitution)
        j = -(1 + e) * relative_velocity.dot(normal)
        j /= bodyA.inv_mass + bodyB.inv_mass

        impulse = j * normal

        bodyA.linear_velocity -= impulse * bodyA.inv_mass
        bodyB.linear_velocity += impulse * bodyB.inv_mass
