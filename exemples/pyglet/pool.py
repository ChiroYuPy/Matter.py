from pyglet import shapes, image
from pyglet.clock import schedule_interval
from pyglet.window import Window, mouse
from pyglet.app import run
from typing import List, Optional, Tuple

from body import Body
from matter import Matter
from shape import Circle, ShapeType, Box
from vector import Vector2
from world import World

# Constants
TABLE_WIDTH = 256
TABLE_HEIGHT = 510
WALL_THICKNESS = 20
BALL_RADIUS = 8
NUM_BALLS = 24
MIN_CUE_LENGTH = 10
MAX_CUE_LENGTH = 100
POCKET_RADIUS = 24


class Game:
    def __init__(self) -> None:
        self.world = World(gravity=Vector2(0, 0), damping=0.1)

        self.background_image = image.load('../assets/images/pool_table.png')
        self.background_texture = self.background_image.get_texture()
        self.window = Window(self.background_texture.width, self.background_texture.height, "Pool Game")

        self.center_x = self.window.width // 2
        self.center_y = self.window.height // 2

        schedule_interval(self.update, 1 / 60)

        self.cue = self.Cue(self)

        self.setup_event_handlers()

        self.initialize_table_walls()

        self.initialize_balls()

        self.pockets = self.define_pockets()

    def setup_event_handlers(self) -> None:
        """Sets up event handlers for the window."""
        self.window.push_handlers(
            on_draw=self.on_draw,
            on_mouse_press=self.cue.on_mouse_press,
            on_mouse_drag=self.cue.on_mouse_drag,
            on_mouse_release=self.cue.on_mouse_release
        )

    def initialize_table_walls(self) -> None:
        """Initializes the walls of the pool table."""
        wall_matter = Matter(density=0, friction=1, color=(64, 64, 64))

        walls = [
            Body(Box(TABLE_WIDTH + WALL_THICKNESS, WALL_THICKNESS), wall_matter, self.center_x,
                 self.center_y + TABLE_HEIGHT / 2, is_static=True),
            Body(Box(TABLE_WIDTH + WALL_THICKNESS, WALL_THICKNESS), wall_matter, self.center_x,
                 self.center_y - TABLE_HEIGHT / 2, is_static=True),
            Body(Box(WALL_THICKNESS, TABLE_HEIGHT - WALL_THICKNESS), wall_matter, self.center_x + TABLE_WIDTH / 2,
                 self.center_y, is_static=True),
            Body(Box(WALL_THICKNESS, TABLE_HEIGHT - WALL_THICKNESS), wall_matter, self.center_x - TABLE_WIDTH / 2,
                 self.center_y, is_static=True)
        ]

        self.world.add_body(walls)

    def initialize_balls(self) -> None:
        """Initializes the balls and their positions on the table."""
        cue_ball_position = Vector2(self.center_x, self.center_y - 200)
        triangle_center = Vector2(self.center_x, self.center_y + 100)
        triangle_positions = self.triangle_positions(triangle_center, BALL_RADIUS, NUM_BALLS)

        matter_list = [
            Matter(density=1, friction=0.6, color=(0, 0, 0)),  # Black
            Matter(density=1, friction=0.6, color=(255, 213, 0)),  # Yellow
            Matter(density=1, friction=0.6, color=(205, 0, 0))  # Red
        ]
        ball_order = [2, 2, 1, 1, 0, 2, 2, 1, 2, 1, 1, 2, 1, 1, 2]

        for i, position in enumerate(triangle_positions):
            matter = matter_list[ball_order[i]]
            ball = Body(Circle(BALL_RADIUS), matter, position.x, position.y)
            self.world.add_body(ball)

        self.cue_ball = Body(Circle(BALL_RADIUS), Matter(density=1, friction=0.6, color=(240, 240, 240)),
                             cue_ball_position.x, cue_ball_position.y)
        self.world.add_body(self.cue_ball)

    def triangle_positions(self, center: Vector2, radius: float, num_balls: int) -> List[Vector2]:
        """
        Calculates the positions of balls in a triangular arrangement.

        Args:
            center: Center position of the triangle.
            radius: Radius of each ball.
            num_balls: Total number of balls.

        Returns:
            List of positions for the balls.
        """
        positions = []
        rows = int((num_balls + 1) ** 0.5)  # Estimate number of rows
        for row in range(rows):
            for col in range(row + 1):
                x = center.x + (col - row / 2) * 2 * radius
                y = center.y + row * 1.5 * radius
                positions.append(Vector2(x, y))
        return positions

    def define_pockets(self) -> List[Vector2]:
        """Defines the positions of the pockets on the table."""
        return [
            Vector2(self.center_x - TABLE_WIDTH / 2, self.center_y - TABLE_HEIGHT / 2),
            Vector2(self.center_x + TABLE_WIDTH / 2, self.center_y - TABLE_HEIGHT / 2),
            Vector2(self.center_x - TABLE_WIDTH / 2, self.center_y + TABLE_HEIGHT / 2),
            Vector2(self.center_x + TABLE_WIDTH / 2, self.center_y + TABLE_HEIGHT / 2),
            Vector2(self.center_x - TABLE_WIDTH / 2, self.center_y),
            Vector2(self.center_x + TABLE_WIDTH / 2, self.center_y)
        ]

    def ball_in_pocket(self, ball_position: Vector2) -> bool:
        """Checks if a ball is in a pocket."""
        for pocket in self.pockets:
            if (ball_position - pocket).length_squared() < POCKET_RADIUS ** 2:
                return True
        return False

    def update(self, dt: float) -> None:
        """Updates the game state."""
        self.world.step(dt, iterations=8)
        # Check for balls in pockets
        balls_to_remove = []
        for body in self.world.bodies:
            if body.shape.type == ShapeType.CIRCLE:
                if self.ball_in_pocket(body.position):
                    balls_to_remove.append(body)
                    # If it's the cue_ball, we need to reset it
                    if body == self.cue_ball:
                        self.reset_cue_ball()

        # Remove balls from the world
        for ball in balls_to_remove:
            self.world.remove_body(ball)

    def reset_cue_ball(self) -> None:
        """Resets the cue ball to its initial position."""
        self.world.remove_body(self.cue_ball)
        cue_ball_position = Vector2(self.center_x, self.center_y - 200)
        self.cue_ball = Body(Circle(BALL_RADIUS), Matter(density=1, friction=0.6, color=(240, 240, 240)),
                             cue_ball_position.x, cue_ball_position.y)
        self.world.add_body(self.cue_ball)

    def on_draw(self) -> None:
        """Draws the game elements on the window."""
        self.window.clear()
        self.background_image.blit(0, 0)

        # Draw balls
        for body in self.world.bodies:
            if body.shape.type == ShapeType.CIRCLE:
                shapes.Circle(body.position.x, body.position.y, body.shape.radius, color=body.matter.color).draw()

        # Draw cue
        if self.cue.start_pos:
            ball_pos = self.cue_ball.position
            cursor_pos = self.cue.start_pos

            # Compute the vector from ball to cursor
            direction = cursor_pos - ball_pos
            direction_length = min(direction.length(), MAX_CUE_LENGTH)  # Limit the length to 100
            normalized_direction = direction.normalize()

            # Compute the end position of the preview line
            preview_end_pos = ball_pos + normalized_direction * -direction_length * 4

            # Draw the cue line
            shapes.Line(ball_pos.x, ball_pos.y, cursor_pos.x, cursor_pos.y, width=4, color=(64, 64, 64)).draw()

            # Draw the preview line
            shapes.Line(ball_pos.x, ball_pos.y, preview_end_pos.x, preview_end_pos.y, width=1,
                        color=(128, 128, 128)).draw()

    class Cue:
        def __init__(self, game: 'Game') -> None:
            self.game = game
            self.start_pos: Optional[Vector2] = None

        def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
            """Handles mouse press events."""
            if button == mouse.LEFT:
                self.start_pos = Vector2(x, y)

        def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int) -> None:
            """Handles mouse drag events."""
            if buttons & mouse.LEFT and self.start_pos:
                ball_pos = self.game.cue_ball.position
                cursor_pos = Vector2(x, y)

                # Compute the vector from ball to cursor
                direction = cursor_pos - ball_pos
                length = min(max(direction.length(), MIN_CUE_LENGTH), MAX_CUE_LENGTH)
                normalized_direction = direction.normalize()

                # Update the start position of the cue
                self.start_pos = ball_pos + normalized_direction * length

        def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
            """Handles mouse release events."""
            if button == mouse.LEFT:
                if self.start_pos:
                    ball_pos = self.game.cue_ball.position
                    cursor_pos = Vector2(x, y)

                    # Compute the force to apply
                    impulse = (cursor_pos - ball_pos).normalize() * min((cursor_pos - ball_pos).length(),
                                                                        MAX_CUE_LENGTH)
                    self.game.cue_ball.apply_impulse(-impulse * 5)

                self.start_pos = None


if __name__ == "__main__":
    game = Game()
    run()
