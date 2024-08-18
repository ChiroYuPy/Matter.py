from vector import Vector2


class Camera:
    def __init__(self, center_x, center_y):
        self.center = Vector2(center_x, center_y)
        self.pos = Vector2()
        self.zoom = 1
        self.min_zoom = 0.4
        self.max_zoom = 4

    def world_to_screen(self, x, y):
        nx = (x - self.pos.x) * self.zoom + self.center.x
        ny = (y - self.pos.y) * self.zoom + self.center.y
        return nx, ny

    def screen_to_world(self, x, y):
        nx = (x - self.center.x) / self.zoom + self.pos.x
        ny = (y - self.center.y) / self.zoom + self.pos.y
        return nx, ny

    def zoom_in(self):
        self.zoom *= 1.1
        self.zoom = min(self.max_zoom, self.zoom)

    def zoom_out(self):
        self.zoom /= 1.1
        self.zoom = max(self.min_zoom, self.zoom)

    def move(self, dx, dy):
        self.pos.x += dx
        self.pos.y += dy