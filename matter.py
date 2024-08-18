class Matter:
    def __init__(self, density: float = 1.0, restitution: float = 1.0, color: tuple[int, int, int] or tuple[int, int, int, int] = (255, 255, 255)):
        self.density = density
        self.restitution = restitution
        self.color = color