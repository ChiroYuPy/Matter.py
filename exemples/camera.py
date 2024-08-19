from vector import Vector2


class Camera:
    def __init__(self, center_x=0.0, center_y=0.0, min_zoom=0.4, max_zoom=4):
        self.center = Vector2(center_x, center_y)
        self.pos = Vector2()
        self.zoom = 1
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom

    def set_center(self, x, y):
        self.center.x = x
        self.center.y = y

    def world_to_screen(self, x, y):
        nx = (x - self.pos.x) * self.zoom + self.center.x
        ny = (y - self.pos.y) * self.zoom + self.center.y
        return nx, ny

    def screen_to_world(self, x, y):
        nx = (x - self.center.x) / self.zoom + self.pos.x
        ny = (y - self.center.y) / self.zoom + self.pos.y
        return nx, ny

    def zoom_in(self, x=None, y=None):
        if x is None or y is None:
            # Utiliser le centre de l'écran comme point de zoom par défaut
            x, y = self.center.x, self.center.y

        # Calculez le point du monde avant le zoom
        world_x, world_y = self.screen_to_world(x, y)

        # Augmentez le zoom
        self.zoom *= 1.1
        self.zoom = min(self.max_zoom, self.zoom)

        # Calculez la nouvelle position de la caméra pour que le point du monde reste fixe
        new_x, new_y = self.screen_to_world(x, y)
        self.pos.x += (world_x - new_x)
        self.pos.y += (world_y - new_y)

    def zoom_out(self, x=None, y=None):
        if x is None or y is None:
            # Utiliser le centre de l'écran comme point de zoom par défaut
            x, y = self.center.x, self.center.y

        # Calculez le point du monde avant le zoom
        world_x, world_y = self.screen_to_world(x, y)

        # Réduisez le zoom
        self.zoom /= 1.1
        self.zoom = max(self.min_zoom, self.zoom)

        # Calculez la nouvelle position de la caméra pour que le point du monde reste fixe
        new_x, new_y = self.screen_to_world(x, y)
        self.pos.x += (world_x - new_x)
        self.pos.y += (world_y - new_y)

    def move(self, dx, dy):
        self.pos.x += dx
        self.pos.y += dy

    def get_extends(self):
        left, top = self.screen_to_world(0, 0)
        right, bottom = self.screen_to_world(self.center.x * 2, self.center.y * 2)
        return left, right, bottom, top
