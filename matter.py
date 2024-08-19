class Matter:
    def __init__(self, density: float = 1.0, friction: float = 0.5, restitution: float = 1, color: tuple[int, int, int] or tuple[int, int, int, int] = (255, 255, 255)):
        self.density = density
        self.restitution = restitution
        self.color = color
        self.static_friction = friction
        self.dynamic_friction = friction

        if density < 0:
            raise ValueError("Density must be a positive value.")

        if restitution < 0:
            raise ValueError("Restitution must be a positive value.")

        if friction < 0 or friction > 1:
            raise ValueError("Friction must be a value between 0 and 1.")