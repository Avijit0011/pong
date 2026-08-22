import random
import pygame

class Particle:
    def __init__(self, x, y, vx, vy, color, size, lifespan, shape="circle"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.max_lifespan = lifespan
        self.lifespan = lifespan
        self.shape = shape

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.96  # Drag
        self.vy *= 0.96
        self.lifespan -= 1

    def draw(self, surface):
        if self.lifespan <= 0:
            return
        
        alpha_ratio = max(0.0, self.lifespan / self.max_lifespan)
        current_size = max(1, int(self.size * alpha_ratio))
        
        r, g, b = self.color[:3]
        color_with_alpha = (r, g, b, int(255 * alpha_ratio))
        
        # Create temporary alpha surface for soft glow particles
        surf_size = current_size * 4
        particle_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        center = (surf_size // 2, surf_size // 2)
        
        # Outer glow
        glow_color = (r, g, b, int(100 * alpha_ratio))
        pygame.draw.circle(particle_surf, glow_color, center, surf_size // 2)
        # Core particle
        pygame.draw.circle(particle_surf, color_with_alpha, center, current_size)
        
        surface.blit(particle_surf, (self.x - surf_size // 2, self.y - surf_size // 2))

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.lifespan > 0]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

    def spawn_impact_sparks(self, x, y, direction_x, color=(0, 245, 255), count=25):
        for _ in range(count):
            angle_speed_x = direction_x * random.uniform(2.0, 9.0)
            speed_y = random.uniform(-6.0, 6.0)
            size = random.uniform(3, 7)
            lifespan = random.randint(15, 35)
            self.particles.append(Particle(x, y, angle_speed_x, speed_y, color, size, lifespan))

    def spawn_goal_explosion(self, x, y, color=(255, 0, 128), count=60):
        for _ in range(count):
            angle = random.uniform(0, 6.28318)
            speed = random.uniform(3.0, 14.0)
            vx = math_cos(angle) * speed
            vy = math_sin(angle) * speed
            size = random.uniform(4, 9)
            lifespan = random.randint(25, 55)
            self.particles.append(Particle(x, y, vx, vy, color, size, lifespan))

    def spawn_powerup_sparkles(self, x, y, color=(255, 215, 0), count=30):
        for _ in range(count):
            angle = random.uniform(0, 6.28318)
            speed = random.uniform(1.5, 6.0)
            vx = math_cos(angle) * speed
            vy = math_sin(angle) * speed
            size = random.uniform(3, 6)
            lifespan = random.randint(20, 40)
            self.particles.append(Particle(x, y, vx, vy, color, size, lifespan))

def math_cos(rad):
    import math
    return math.cos(rad)

def math_sin(rad):
    import math
    return math.sin(rad)
