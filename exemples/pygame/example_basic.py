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

# pyglet imports
from pyglet import shapes
from pyglet.clock import schedule_interval
from pyglet.window import Window
from pyglet.app import run

# Matter.py imports
from body import Body
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


################################# Pyglet Initialization #################################

# window creation
window = Window(800, 600, "Matter.py")

# update world
def update(dt):
    world.step(dt, iterations=8)

schedule_interval(update, 1/60)

# draw bodies
@window.event
def on_draw():
    window.clear()

    for body in world.bodies:

        if body.shape.type == ShapeType.CIRCLE:
            shapes.Circle(body.position.x, body.position.y, body.shape.radius, color=body.matter.color).draw()

        elif body.shape.type == ShapeType.BOX:
            box_shape = shapes.Rectangle(body.position.x, body.position.y, body.shape.width, body.shape.height, color=body.matter.color)
            box_shape.anchor_position = body.shape.width / 2, body.shape.height / 2
            box_shape.rotation = -math.degrees(body.angle)
            box_shape.draw()

# run the app
run()
