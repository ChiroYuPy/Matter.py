from shape import ShapeType
from vector import Vector2


class Collisions:

    @staticmethod
    def Collide(bodyA, bodyB):
        is_collided = False
        normal = Vector2()
        depth = 0

        if bodyA.shape.type is ShapeType.BOX:
            if bodyB.shape.type is ShapeType.BOX:
                is_collided, normal, depth = Collisions.IntersectPolygons(
                    bodyA.position, bodyA.get_transformed_vertices(),
                    bodyB.position, bodyB.get_transformed_vertices())

            elif bodyB.shape.type is ShapeType.CIRCLE:
                is_collided, normal, depth = Collisions.IntersectCirclePolygon(
                    bodyB.position, bodyB.shape.radius,
                    bodyA.position, bodyA.get_transformed_vertices())
                normal = -normal

        elif bodyA.shape.type is ShapeType.CIRCLE:
            if bodyB.shape.type is ShapeType.BOX:
                is_collided, normal, depth = Collisions.IntersectCirclePolygon(
                    bodyA.position, bodyA.shape.radius,
                    bodyB.position, bodyB.get_transformed_vertices())

            elif bodyB.shape.type is ShapeType.CIRCLE:
                is_collided, normal, depth = Collisions.IntersectCircles(
                    bodyA.position, bodyA.shape.radius,
                    bodyB.position, bodyB.shape.radius)

        return is_collided, normal, depth

    @staticmethod
    def IntersectCirclePolygon(circle_center, circle_radius, polygon_center, polygon_vertices, invert_normal=False):
        normal, depth = Vector2(), float('inf')
        for i in range(len(polygon_vertices)):
            va, vb = polygon_vertices[i], polygon_vertices[(i + 1) % len(polygon_vertices)]
            axis = Vector2(- (vb - va).y, (vb - va).x).normalize()
            minA, maxA = Collisions.ProjectVertices(polygon_vertices, axis)
            minB, maxB = Collisions.ProjectCircle(circle_center, circle_radius, axis)

            if minA >= maxB or minB >= maxA:
                return False, normal, depth

            axis_depth = min(maxB - minA, maxA - minB)
            if axis_depth < depth:
                depth, normal = axis_depth, axis

        cp_index = Collisions.FindClosestPointOnPolygon(circle_center, polygon_vertices)
        cp = polygon_vertices[cp_index]
        axis = (cp - circle_center).normalize()
        minA, maxA = Collisions.ProjectVertices(polygon_vertices, axis)
        minB, maxB = Collisions.ProjectCircle(circle_center, circle_radius, axis)

        if minA >= maxB or minB >= maxA:
            return False, normal, depth

        axis_depth = min(maxB - minA, maxA - minB)
        if axis_depth < depth:
            depth, normal = axis_depth, axis

        direction = polygon_center - circle_center
        if direction.dot(normal) < 0:
            normal = -normal

        if invert_normal:
            normal = -normal

        return True, normal, depth

    @staticmethod
    def FindClosestPointOnPolygon(circle_center, vertices):
        distances = [v.distance(circle_center) for v in vertices]
        return distances.index(min(distances))

    @staticmethod
    def ProjectCircle(center, radius, axis):
        direction = axis.normalize() * radius
        p1, p2 = center + direction, center - direction
        min_proj, max_proj = min(p1.dot(axis), p2.dot(axis)), max(p1.dot(axis), p2.dot(axis))
        return min_proj, max_proj

    @staticmethod
    def IntersectPolygons(centerA, verticesA, centerB, verticesB):
        normal, depth = Vector2(0, 0), float('inf')
        polygons = [(verticesA, centerA), (verticesB, centerB)]

        for vertices, center in polygons:
            for i in range(len(vertices)):
                va, vb = vertices[i], vertices[(i + 1) % len(vertices)]
                axis = Vector2(- (vb - va).y, (vb - va).x).normalize()
                minA, maxA = Collisions.ProjectVertices(verticesA, axis)
                minB, maxB = Collisions.ProjectVertices(verticesB, axis)

                if minA >= maxB or minB >= maxA:
                    return False, normal, depth

                axis_depth = min(maxB - minA, maxA - minB)
                if axis_depth < depth:
                    depth, normal = axis_depth, axis

        direction = polygons[1][1] - polygons[0][1]
        if direction.dot(normal) < 0:
            normal = -normal

        return True, normal, depth

    @staticmethod
    def ProjectVertices(vertices, axis):
        projections = [vertex.dot(axis) for vertex in vertices]
        return min(projections), max(projections)

    @staticmethod
    def IntersectCircles(centerA, radiusA, centerB, radiusB):
        distance = centerA.distance(centerB)
        radii = radiusA + radiusB
        if distance >= radii:
            return False, Vector2(), 0
        normal = (centerB - centerA).normalize()
        depth = radii - distance
        return True, normal, depth