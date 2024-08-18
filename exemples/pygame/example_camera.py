"""
Matter.py Physics Engine Overview

This script implements the Matter.py physics engine to simulate and display a 2D dynamic scene using the Pyglet library. Below is a summary of the main features:

1. **World Initialization**:
   - Creates a physical world with gravity set to -9.81 m/s², simulating Earth's gravity.

2. **Object Creation**:
   - **Dynamic Bodies**: Two dynamic bodies (a circle and a cube) are added to the scene with realistic physical properties.
   - **Static Bodies**: Two static bodies (a ground plane and an inclined slope) act as supports for the dynamic bodies.

3. **Simulation and Rendering**:
   - The simulation updates at a frequency of 60 frames per second for smooth animation.
   - The bodies are rendered on screen with their specific shapes (circle or rectangle) and physical properties (dynamic or static).

4. **Graphical Interface**:
   - The simulation window is 800x600 pixels, displaying the moving bodies according to the physical laws.

The script combines Pyglet for graphical rendering with the Matter.py engine for physical simulation, providing a real-time interactive experience with realistic collisions and movement.

"""

import math

# Pygame imports
import pygame
from pygame.locals import QUIT, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, MOUSEWHEEL

# Matter.py imports
from body import Body
from exemples.camera import Camera
from matter import Matter
from shape import Box, Circle, ShapeType
from vector import Vector2
from world import World

############################### Matter.py Initialization ###############################

# world creation
world = World(gravity=Vector2(0, -9.81))

# shapes creation
circle = Circle(25)
cube = Box(40, 40)

# matter creation
dynamic_matter = Matter(1, color=(127, 160, 80))
static_matter = Matter(color=(64, 64, 64))

# dynamic bodies creation
body1 = Body(circle, dynamic_matter, 400, 400)
body2 = Body(cube, dynamic_matter, 350, 350)

# static bodies creation
ground = Body(Box(768, 16), static_matter, 400, 24, is_static=True)
slope = Body(Box(200, 20), static_matter, 200, 200, is_static=True, angle=math.radians(-30))

# add bodies to the world
world.add_body([body1, body2, ground, slope])

################################# Pygame Initialization #################################

# initialize Pygame
pygame.init()

# window creation
window_size = (800, 600)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Matter.py")


# color definitions
def get_color_tuple(color):
    return (color[0], color[1], color[2])


# camera creation
camera = Camera(window_size[0] / 2, window_size[1] / 2)


# update world
def update(dt):
    world.step(dt, iterations=8)


# main loop
clock = pygame.time.Clock()
running = True
mouse_drag = False

while running:
    dt = clock.tick(60) / 1000.0  # Amount of seconds between each loop
    update(dt)

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 3:  # Right mouse button
                mouse_drag = True
        elif event.type == MOUSEBUTTONUP:
            if event.button == 3:  # Right mouse button
                mouse_drag = False
        elif event.type == MOUSEMOTION:
            if mouse_drag:
                camera.move(-event.rel[0] / camera.zoom, -event.rel[1] / camera.zoom)
        elif event.type == MOUSEWHEEL:
            if event.y > 0:
                camera.zoom_in()
            else:
                camera.zoom_out()

    # clear the screen
    screen.fill((0, 0, 0))

    # draw bodies
    for body in world.bodies:
        color = get_color_tuple(body.matter.color)

        if body.shape.type == ShapeType.CIRCLE:
            nx, ny = camera.world_to_screen(body.position.x, body.position.y)
            pygame.draw.circle(screen, color, (int(nx), int(ny)), int(body.shape.radius * camera.zoom))

        elif body.shape.type == ShapeType.BOX:
            nx, ny = camera.world_to_screen(body.position.x, body.position.y)
            box_rect = pygame.Rect(
                int(nx - body.shape.width * camera.zoom / 2),
                int(ny - body.shape.height * camera.zoom / 2),
                int(body.shape.width * camera.zoom),
                int(body.shape.height * camera.zoom)
            )
            rotated_surf = pygame.Surface(box_rect.size, pygame.SRCALPHA)
            rotated_surf.fill(color)
            rotated_surf = pygame.transform.rotate(rotated_surf, -math.degrees(body.angle))
            screen.blit(rotated_surf, box_rect.topleft)

    # update the display
    pygame.display.flip()

pygame.quit()