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

# Pyglet imports
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

# Create the physical world with gravity
world = World(gravity=Vector2(0, -9.81 * 10))  # Gravity scaled for simulation

# Define shapes for dynamic bodies
circle = Circle(25)  # Circle with a radius of 25
cube = Box(40, 40)   # Square box with width and height of 40

# Define material properties for dynamic and static bodies
dynamic_matter = Matter(density=1, restitution=0.5, color=(127, 160, 80))  # Dynamic bodies
static_matter = Matter(density=0, restitution=0.5, color=(64, 64, 64))    # Static bodies

# Create dynamic bodies and initialize their positions and properties
body1 = Body(circle, dynamic_matter, 400, 400)  # Circle body positioned at (400, 400)
body2 = Body(cube, dynamic_matter, 350, 350, angle=math.radians(30))  # Rotated cube body positioned at (350, 350)

# Create static bodies and set their positions, angles, and static status
ground = Body(Box(768, 16), static_matter, 400, 24, is_static=True)  # Ground plane
slope = Body(Box(200, 20), static_matter, 350, 200, is_static=True, angle=math.radians(-30))  # Inclined slope

# Add all created bodies to the world
world.add_body([body1, body2, ground, slope])

################################# Pyglet Initialization #################################

# Create a Pyglet window for rendering
window = Window(800, 600, "Matter.py Physics Engine")

# Update function to advance the simulation
def update(dt):
    world.step(dt, iterations=8)  # Step the simulation with fixed time step

# Schedule the update function to be called at 60 FPS
schedule_interval(update, 1/60)

# Event handler for drawing the simulation
@window.event
def on_draw():
    window.clear()  # Clear the window before drawing

    for body in world.bodies:
        if body.shape.type == ShapeType.CIRCLE:
            shapes.Circle(body.position.x, body.position.y, body.shape.radius, color=body.matter.color).draw()

        elif body.shape.type == ShapeType.BOX:
            shapes.Polygon(*body.get_vertices(tuple=True), color=body.matter.color).draw()

# Event handler for mouse clicks to create new bodies
@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == 1:  # Left mouse button
        body = Body(circle, dynamic_matter, x, y)  # Create and add a circle body
        world.add_body(body)

    elif button == 4:  # Right mouse button
        body = Body(cube, dynamic_matter, x, y)  # Create and add a cube body
        world.add_body(body)

# Start the Pyglet application
run()
