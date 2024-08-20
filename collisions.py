import math

from shape import ShapeType
from vector import Vector2


class Collisions:
    @staticmethod
    def point_segment_distance(p, a, b):
        ab = b - a
        ap = p - a

        proj = Vector2.dot(ap, ab)
        ab_len_sq = Vector2.length_squared(ab)
        d = proj / ab_len_sq

        if d <= 0:
            cp = a
        elif d >= 1:
            cp = b
        else:
            cp = a + ab * d

        distance_squared = Vector2.distance_squared(p, cp)
        return distance_squared, cp

    @staticmethod
    def intersect_aabbs(a, b):
        if (a.max.x <= b.min.x or b.max.x <= a.min.x or
                a.max.y <= b.min.y or b.max.y <= a.min.y):
            return False
        return True

    @staticmethod
    def find_contact_points(bodyA, bodyB):
        contact1 = Vector2()
        contact2 = Vector2()
        contact_count = 0

        shape_type_a = bodyA.shape.type
        shape_type_b = bodyB.shape.type

        if shape_type_a == ShapeType.BOX or shape_type_a == ShapeType.POLYGON:
            if shape_type_b == ShapeType.BOX or shape_type_b == ShapeType.POLYGON:
                contact1, contact2, contact_count = Collisions.find_polygons_contact_points(
                    bodyA.get_transformed_vertices(), bodyB.get_transformed_vertices())
            elif shape_type_b == ShapeType.CIRCLE:
                contact1 = Collisions.find_circle_polygon_contact_point(
                    bodyB.position, bodyB.shape.radius, bodyA.position, bodyA.get_transformed_vertices())
                contact_count = 1
        elif shape_type_a == ShapeType.CIRCLE:
            if shape_type_b == ShapeType.BOX or shape_type_b == ShapeType.POLYGON:
                contact1 = Collisions.find_circle_polygon_contact_point(
                    bodyA.position, bodyA.shape.radius, bodyB.position, bodyB.get_transformed_vertices())
                contact_count = 1
            elif shape_type_b == ShapeType.CIRCLE:
                contact1 = Collisions.find_circles_contact_point(
                    bodyA.position, bodyA.shape.radius, bodyB.position)
                contact_count = 1

        return contact1, contact2, contact_count

    @staticmethod
    def nearly_equal(vec1, vec2, rel_tol=1e-9, abs_tol=1e-9):
        return (math.isclose(vec1.x, vec2.x, rel_tol=rel_tol, abs_tol=abs_tol) and
                math.isclose(vec1.y, vec2.y, rel_tol=rel_tol, abs_tol=abs_tol))

    @staticmethod
    def find_polygons_contact_points(vertices_a, vertices_b):
        contact1 = Vector2()
        contact2 = Vector2()
        contact_count = 0

        min_dist_sq = float('inf')

        for p in vertices_a:
            for i in range(len(vertices_b)):
                va = vertices_b[i]
                vb = vertices_b[(i + 1) % len(vertices_b)]

                dist_sq, cp = Collisions.point_segment_distance(p, va, vb)

                if math.isclose(dist_sq, min_dist_sq):
                    if not Collisions.nearly_equal(cp, contact1):
                        contact2 = cp
                        contact_count = 2
                elif dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    contact_count = 1
                    contact1 = cp

        for p in vertices_b:
            for i in range(len(vertices_a)):
                va = vertices_a[i]
                vb = vertices_a[(i + 1) % len(vertices_a)]

                dist_sq, cp = Collisions.point_segment_distance(p, va, vb)

                if math.isclose(dist_sq, min_dist_sq):
                    if not Collisions.nearly_equal(cp, contact1):
                        contact2 = cp
                        contact_count = 2
                elif dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    contact_count = 1
                    contact1 = cp

        return contact1, contact2, contact_count

    @staticmethod
    def find_circle_polygon_contact_point(circle_center, circle_radius, polygon_center, polygon_vertices):
        cp = Vector2()
        min_dist_sq = float('inf')

        for i in range(len(polygon_vertices)):
            va = polygon_vertices[i]
            vb = polygon_vertices[(i + 1) % len(polygon_vertices)]

            dist_sq, contact = Collisions.point_segment_distance(circle_center, va, vb)

            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                cp = contact

        return cp

    @staticmethod
    def find_circles_contact_point(center_a, radius_a, center_b):
        ab = center_b - center_a
        dir = Vector2.normalize(ab)
        cp = center_a + dir * radius_a
        return cp

    @staticmethod
    def collide(body_a, body_b):
        normal = Vector2()
        depth = 0.0

        shape_type_a = body_a.shape.type
        shape_type_b = body_b.shape.type

        if shape_type_a == ShapeType.BOX or shape_type_a == ShapeType.POLYGON:
            if shape_type_b == ShapeType.BOX or shape_type_b == ShapeType.POLYGON:
                return Collisions.intersect_polygons(
                    body_a.position, body_a.get_transformed_vertices(),
                    body_b.position, body_b.get_transformed_vertices())
            elif shape_type_b == ShapeType.CIRCLE:
                result, normal, depth = Collisions.intersect_circle_polygon(
                    body_b.position, body_b.shape.radius,
                    body_a.position, body_a.get_transformed_vertices())
                normal = -normal
                return result, normal, depth
        elif shape_type_a == ShapeType.CIRCLE:
            if shape_type_b == ShapeType.BOX or shape_type_b == ShapeType.POLYGON:
                return Collisions.intersect_circle_polygon(
                    body_a.position, body_a.shape.radius,
                    body_b.position, body_b.get_transformed_vertices())
            elif shape_type_b == ShapeType.CIRCLE:
                return Collisions.intersect_circles(
                    body_a.position, body_a.shape.radius,
                    body_b.position, body_b.shape.radius)

        return False, normal, depth

    @staticmethod
    def intersect_circle_polygon(circle_center, circle_radius, polygon_center, vertices):
        normal = Vector2()
        depth = float('inf')

        for i in range(len(vertices)):
            va = vertices[i]
            vb = vertices[(i + 1) % len(vertices)]

            edge = vb - va
            axis = Vector2(-edge.y, edge.x)
            axis = Vector2.normalize(axis)

            min_a, max_a = Collisions.project_vertices(vertices, axis)
            min_b, max_b = Collisions.project_circle(circle_center, circle_radius, axis)

            if min_a >= max_b or min_b >= max_a:
                return False, normal, depth

            axis_depth = min(max_b - min_a, max_a - min_b)

            if axis_depth < depth:
                depth = axis_depth
                normal = axis

        cp_index = Collisions.find_closest_point_on_polygon(circle_center, vertices)
        cp = vertices[cp_index]

        axis = cp - circle_center
        axis = Vector2.normalize(axis)

        min_a, max_a = Collisions.project_vertices(vertices, axis)
        min_b, max_b = Collisions.project_circle(circle_center, circle_radius, axis)

        if min_a >= max_b or min_b >= max_a:
            return False, normal, depth

        axis_depth = min(max_b - min_a, max_a - min_b)

        if axis_depth < depth:
            depth = axis_depth
            normal = axis

        direction = polygon_center - circle_center

        if Vector2.dot(direction, normal) < 0:
            normal = -normal

        return True, normal, depth

    @staticmethod
    def find_closest_point_on_polygon(circle_center, vertices):
        result = -1
        min_distance = float('inf')

        for i in range(len(vertices)):
            v = vertices[i]
            distance = Vector2.distance(v, circle_center)

            if distance < min_distance:
                min_distance = distance
                result = i

        return result

    @staticmethod
    def project_circle(center, radius, axis):
        direction = Vector2.normalize(axis)
        direction_and_radius = direction * radius

        p1 = center + direction_and_radius
        p2 = center - direction_and_radius

        min_proj = Vector2.dot(p1, axis)
        max_proj = Vector2.dot(p2, axis)

        if min_proj > max_proj:
            min_proj, max_proj = max_proj, min_proj

        return min_proj, max_proj

    @staticmethod
    def intersect_polygons(center_a, vertices_a, center_b, vertices_b):
        normal = Vector2()
        depth = float('inf')

        for i in range(len(vertices_a)):
            va = vertices_a[i]
            vb = vertices_a[(i + 1) % len(vertices_a)]

            edge = vb - va
            axis = Vector2(-edge.y, edge.x)
            axis = Vector2.normalize(axis)

            min_a, max_a = Collisions.project_vertices(vertices_a, axis)
            min_b, max_b = Collisions.project_vertices(vertices_b, axis)

            if min_a >= max_b or min_b >= max_a:
                return False, normal, depth

            axis_depth = min(max_b - min_a, max_a - min_b)

            if axis_depth < depth:
                depth = axis_depth
                normal = axis

        for i in range(len(vertices_b)):
            va = vertices_b[i]
            vb = vertices_b[(i + 1) % len(vertices_b)]

            edge = vb - va
            axis = Vector2(-edge.y, edge.x)
            axis = Vector2.normalize(axis)

            min_a, max_a = Collisions.project_vertices(vertices_a, axis)
            min_b, max_b = Collisions.project_vertices(vertices_b, axis)

            if min_a >= max_b or min_b >= max_a:
                return False, normal, depth

            axis_depth = min(max_b - min_a, max_a - min_b)

            if axis_depth < depth:
                depth = axis_depth
                normal = axis

        direction = center_b - center_a

        if Vector2.dot(direction, normal) < 0:
            normal = -normal

        return True, normal, depth

    @staticmethod
    def project_vertices(vertices, axis):
        min_proj = float('inf')
        max_proj = float('-inf')

        for v in vertices:
            proj = Vector2.dot(v, axis)
            if proj < min_proj:
                min_proj = proj
            if proj > max_proj:
                max_proj = proj

        return min_proj, max_proj

    @staticmethod
    def intersect_circles(center_a, radius_a, center_b, radius_b):
        normal = Vector2()
        depth = 0.0

        distance = Vector2.distance(center_a, center_b)
        radii = radius_a + radius_b

        if distance >= radii:
            return False, normal, depth

        normal = Vector2.normalize(center_b - center_a)
        depth = radii - distance

        return True, normal, depth