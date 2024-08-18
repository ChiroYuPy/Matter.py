import math


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
