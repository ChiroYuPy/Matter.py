from typing import Union, List
from body import Body
from collisions import Collisions
from manifold import Manifold
from vector import Vector2

class World:
    MIN_ITERATIONS = 1
    MAX_ITERATIONS = 16

    def __init__(self, gravity: Vector2 = Vector2(0, -9.81), damping: float = 0.0):
        self.gravity = gravity
        self.damping = damping
        self.bodies: List[Body] = []
        self.contact_pairs: List[(int, int)] = []

        self.contact_points: List[tuple[int, int]] = []

        self.contact_list: List[Vector2] = []
        self.impulse_list: List[Vector2] = []
        self.ra_list: List[Vector2] = []
        self.rb_list: List[Vector2] = []
        self.friction_impulse_list: List[Vector2] = []
        self.j_list: List[float] = []

    @property
    def body_count(self) -> int:
        return len(self.bodies)

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
        if index < 0 or index >= self.body_count:
            raise IndexError("Body index out of range.")
        return self.bodies[index]

    def get_body_by_position(self, x, y):
        for body in self.bodies:
            if body.shape.contains_point(body.position, Vector2(x, y)):
                return body
        return None

    def step(self, dt: float, iterations: int = 1):

        iterations = max(min(iterations, self.MAX_ITERATIONS), self.MIN_ITERATIONS)

        for _ in range(iterations):
            self.contact_list.clear()
            self.step_bodies(dt, iterations)
            self.broad_phase()
            self.narrow_phase()

    def broad_phase(self):
        self.contact_pairs.clear()
        for i in range(self.body_count - 1):
            bodyA = self.bodies[i]
            bodyA.AABB = bodyA.get_AABB()

            for j in range(i + 1, self.body_count):
                bodyB = self.bodies[j]
                bodyB.AABB = bodyB.get_AABB()

                if bodyA.is_static and bodyB.is_static:
                    continue

                if not Collisions.intersect_aabbs(bodyA.AABB, bodyB.AABB):
                    continue

                self.contact_pairs.append((i, j))

    def narrow_phase(self):
        for pair in self.contact_pairs:
            i, j = pair
            bodyA = self.bodies[i]
            bodyB = self.bodies[j]

            collision, normal, depth = Collisions.collide(bodyA, bodyB)

            if collision:

                self.separate_bodies(bodyA, bodyB, normal * depth)
                contact1, contact2, contact_count = Collisions.find_contact_points(bodyA, bodyB)
                contact = Manifold(bodyA, bodyB, normal, depth, contact1, contact2, contact_count)
                # self.resolve_collision_basic(contact)
                self.resolve_collision_with_rotation_and_friction(contact)

    def step_bodies(self, dt: float, total_iterations: int):
        for body in self.bodies:
            body.linear_velocity *= 1 - self.damping * dt
            body.step(dt, self.gravity, total_iterations)

    @staticmethod
    def separate_bodies(bodyA, bodyB, mtv):
        if bodyA.is_static:
            bodyB.move(mtv)
        elif bodyB.is_static:
            bodyA.move(-mtv)
        else:
            bodyA.move(-mtv / 2)
            bodyB.move(mtv / 2)

    @staticmethod
    def resolve_collision(contact: Manifold):

        bodyA = contact.bodyA
        bodyB = contact.bodyB
        normal = contact.normal

        relative_velocity = bodyB.linear_velocity - bodyA.linear_velocity

        if relative_velocity.dot(normal) > 0.0:
            return

        e = min(bodyA.matter.restitution, bodyB.matter.restitution)
        j = - (1.0 + e) * relative_velocity.dot(normal)
        j = j / (bodyA.inv_mass + bodyB.inv_mass)

        impulse = j * normal

        bodyA.linear_velocity -= impulse * bodyA.inv_mass
        bodyB.linear_velocity += impulse * bodyB.inv_mass

    def resolve_collision_with_rotation(self, contact: Manifold):
        body_a = contact.bodyA
        body_b = contact.bodyB
        normal = contact.normal
        contact1 = contact.contact1
        contact2 = contact.contact2
        contact_count = contact.contact_count

        e = min(body_a.matter.restitution, body_b.matter.restitution)

        self.contact_list = [contact1, contact2]

        self.impulse_list = [Vector2() for _ in range(contact_count)]
        self.ra_list = [Vector2() for _ in range(contact_count)]
        self.rb_list = [Vector2() for _ in range(contact_count)]

        for i in range(contact_count):
            ra = self.contact_list[i] - body_a.position
            rb = self.contact_list[i] - body_b.position

            self.ra_list[i] = ra
            self.rb_list[i] = rb

            ra_perp = Vector2(-ra.y, ra.x)
            rb_perp = Vector2(-rb.y, rb.x)

            angular_linear_velocity_a = ra_perp * body_a.angular_velocity
            angular_linear_velocity_b = rb_perp * body_b.angular_velocity

            relative_velocity = (body_b.linear_velocity + angular_linear_velocity_b) - \
                                (body_a.linear_velocity + angular_linear_velocity_a)

            contact_velocity_mag = relative_velocity.dot(normal)

            if contact_velocity_mag > 0:
                continue

            ra_perp_dot_n = ra_perp.dot(normal)
            rb_perp_dot_n = rb_perp.dot(normal)

            denom = (body_a.inv_mass + body_b.inv_mass +
                     (ra_perp_dot_n * ra_perp_dot_n) * body_a.inv_inertia +
                     (rb_perp_dot_n * rb_perp_dot_n) * body_b.inv_inertia)

            j = -(1.0 + e) * contact_velocity_mag
            j /= denom
            j /= contact_count

            impulse = normal * j
            self.impulse_list[i] = impulse

        for i in range(contact_count):
            impulse = self.impulse_list[i]
            ra = self.ra_list[i]
            rb = self.rb_list[i]

            body_a.linear_velocity -= impulse * body_a.inv_mass
            body_a.angular_velocity -= ra.cross(impulse) * body_a.inv_inertia
            body_b.linear_velocity += impulse * body_b.inv_mass
            body_b.angular_velocity += rb.cross(impulse) * body_b.inv_inertia

    def resolve_collision_with_rotation_and_friction(self, contact: Manifold):
        bodyA = contact.bodyA
        bodyB = contact.bodyB
        normal = contact.normal
        contact1 = contact.contact1
        contact2 = contact.contact2
        contact_count = contact.contact_count

        e = min(bodyA.matter.restitution, bodyB.matter.restitution)

        sf = (bodyA.matter.static_friction + bodyB.matter.static_friction) * 0.5
        df = (bodyA.matter.dynamic_friction + bodyB.matter.dynamic_friction) * 0.5

        self.contact_list = [contact1, contact2]

        self.impulse_list = [Vector2() for _ in range(contact_count)]
        self.ra_list = [Vector2() for _ in range(contact_count)]
        self.rb_list = [Vector2() for _ in range(contact_count)]
        self.friction_impulse_list = [Vector2() for _ in range(contact_count)]
        self.j_list = [0.0 for _ in range(contact_count)]

        for i in range(contact_count):
            ra = self.contact_list[i] - bodyA.position
            rb = self.contact_list[i] - bodyB.position

            self.ra_list[i] = ra
            self.rb_list[i] = rb

            ra_perp = Vector2(-ra.y, ra.x)
            rb_perp = Vector2(-rb.y, rb.x)

            angular_linear_velocityA = ra_perp * bodyA.angular_velocity
            angular_linear_velocityB = rb_perp * bodyB.angular_velocity

            relative_velocity = ((bodyB.linear_velocity + angular_linear_velocityB) -
                                 (bodyA.linear_velocity + angular_linear_velocityA))

            contact_velocity_mag = relative_velocity.dot(normal)

            if contact_velocity_mag > 0:
                continue

            ra_perp_dot_normal = ra_perp.dot(normal)
            rb_perp_dot_normal = rb_perp.dot(normal)

            denominator = (bodyA.inv_mass + bodyB.inv_mass +
                           (ra_perp_dot_normal ** 2) * bodyA.inv_inertia +
                           (rb_perp_dot_normal ** 2) * bodyB.inv_inertia)

            j = -(1.0 + e) * contact_velocity_mag
            j /= denominator
            j /= contact_count

            self.j_list[i] = j

            impulse = j * normal
            self.impulse_list[i] = impulse

        for i in range(contact_count):
            impulse = self.impulse_list[i]
            ra = self.ra_list[i]
            rb = self.rb_list[i]

            bodyA.linear_velocity -= impulse * bodyA.inv_mass
            bodyA.angular_velocity -= ra.cross(impulse) * bodyA.inv_inertia
            bodyB.linear_velocity += impulse * bodyB.inv_mass
            bodyB.angular_velocity += rb.cross(impulse) * bodyB.inv_inertia

        for i in range(contact_count):
            ra = self.ra_list[i]
            rb = self.rb_list[i]

            ra_perp = Vector2(-ra.y, ra.x)
            rb_perp = Vector2(-rb.y, rb.x)

            angular_linear_velocityA = ra_perp * bodyA.angular_velocity
            angular_linear_velocityB = rb_perp * bodyB.angular_velocity

            relative_velocity = ((bodyB.linear_velocity + angular_linear_velocityB) -
                                 (bodyA.linear_velocity + angular_linear_velocityA))

            tangent = relative_velocity - relative_velocity.dot(normal) * normal

            if tangent.length_squared() < 1e-6:
                continue
            else:
                tangent = tangent.normalize()

            ra_perp_dot_tangent = ra_perp.dot(tangent)
            rb_perp_dot_tangent = rb_perp.dot(tangent)

            denominator = (bodyA.inv_mass + bodyB.inv_mass +
                           (ra_perp_dot_tangent ** 2) * bodyA.inv_inertia +
                           (rb_perp_dot_tangent ** 2) * bodyB.inv_inertia)

            jt = -relative_velocity.dot(tangent)
            jt /= denominator
            jt /= contact_count

            j = self.j_list[i]

            if abs(jt) <= j * sf:
                friction_impulse = jt * tangent
            else:
                friction_impulse = -j * tangent * df

            self.friction_impulse_list[i] = friction_impulse

        for i in range(contact_count):
            friction_impulse = self.friction_impulse_list[i]
            ra = self.ra_list[i]
            rb = self.rb_list[i]

            bodyA.linear_velocity -= friction_impulse * bodyA.inv_mass
            bodyA.angular_velocity -= ra.cross(friction_impulse) * bodyA.inv_inertia
            bodyB.linear_velocity += friction_impulse * bodyB.inv_mass
            bodyB.angular_velocity += rb.cross(friction_impulse) * bodyB.inv_inertia