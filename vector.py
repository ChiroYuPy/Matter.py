import math

class Vector2:
    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = x
        self.y = y

    def __add__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> 'Vector2':
        return Vector2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> 'Vector2':
        return self.__mul__(scalar)

    def __eq__(self, other: 'Vector2') -> bool:
        return self.x == other.x and self.y == other.y

    def __ne__(self, other: 'Vector2') -> bool:
        return not self.__eq__(other)

    def __neg__(self) -> 'Vector2':
        return Vector2(-self.x, -self.y)

    def __truediv__(self, scalar: float) -> 'Vector2':
        if scalar == 0:
            raise ValueError("Division by zero.")
        return Vector2(self.x / scalar, self.y / scalar)

    def __rtruediv__(self, scalar: float) -> 'Vector2':
        raise NotImplementedError("Scalar division from the right is not supported for Vector2.")

    def __str__(self) -> str:
        return f"({self.x:.2f}, {self.y:.2f})"

    def length(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def length_squared(self) -> float:
        return self.x ** 2 + self.y ** 2

    def normalize(self) -> 'Vector2':
        len_sq = self.length_squared()
        if len_sq == 0:
            return Vector2(0, 0)
        inv_len = 1.0 / math.sqrt(len_sq)
        return self * inv_len

    def distance(self, other: 'Vector2') -> float:
        return (self - other).length()

    def dot(self, other: 'Vector2') -> float:
        return self.x * other.x + self.y * other.y

    def cross(self, other: 'Vector2') -> float:
        return self.x * other.y - self.y * other.x

    def rotate(self, angle: float) -> 'Vector2':
        angle_rad = math.radians(angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        x = self.x * cos_a - self.y * sin_a
        y = self.x * sin_a + self.y * cos_a
        return Vector2(x, y)

    def zero(self) -> None:
        self.x = 0.0
        self.y = 0.0

    @staticmethod
    def transform(v: 'Vector2', transform) -> 'Vector2':
        x = transform.cos * v.x - transform.sin * v.y + transform.position_x
        y = transform.sin * v.x + transform.cos * v.y + transform.position_y
        return Vector2(x, y)
