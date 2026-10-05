import random
import pygame

class Particle:
    """
    Represents a single particle used in visual effects.
    """
    def __init__(self, x, y, vx, vy, color, size, lifespan, shape="circle"):
        pass

    def update(self):
        pass

    def draw(self, surface):
        pass

class ParticleSystem:
    """
    Manages generation, updating, and rendering of multiple particles.
    """
    def __init__(self):
        self.particles = []

    def update(self):
        pass

    def draw(self, surface):
        pass

    def spawn_impact_sparks(self, x, y, direction_x, color=(56, 189, 248), count=8):
        pass

    def spawn_goal_explosion(self, x, y, color=(244, 63, 94), count=24):
        pass

    def spawn_powerup_sparkles(self, x, y, color=(245, 158, 11), count=12):
        pass

    def spawn_speed_trail(self, x, y, color=(56, 189, 248), count=2):
        pass

    def spawn_shockwave(self, x, y, color=(244, 63, 94), max_radius=40):
        pass

def math_cos(rad):
    import math
    return math.cos(rad)

def math_sin(rad):
    import math
    return math.sin(rad)


