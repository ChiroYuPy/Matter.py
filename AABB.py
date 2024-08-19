from vector import Vector2


class AABB:
    def __init__(self, minX, minY, maxX, maxY):
        self.min = Vector2(minX, minY)
        self.max = Vector2(maxX, maxY)