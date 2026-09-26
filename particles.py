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
        self.growth = 0.0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.96  # Drag
        self.vy *= 0.96
        self.lifespan -= 1
        if self.shape == "ring":
            self.size += self.growth

    def draw(self, surface):
        if self.lifespan <= 0:
            return
        
        alpha_ratio = max(0.0, self.lifespan / self.max_lifespan)
        r, g, b = self.color[:3]
        color_with_alpha = (r, g, b, int(220 * alpha_ratio))
        
        if self.shape == "ring":
            cur_r = int(self.size)
            if cur_r > 1:
                surf_size = cur_r * 2 + 6
                ring_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
                center = (surf_size // 2, surf_size // 2)
                pygame.draw.circle(ring_surf, color_with_alpha, center, cur_r, width=2)
                surface.blit(ring_surf, (int(self.x) - surf_size // 2, int(self.y) - surf_size // 2))
            return

        current_size = max(1, int(self.size * alpha_ratio))
        surf_size = current_size * 2 + 2
        particle_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        center = (surf_size // 2, surf_size // 2)
        
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

    def spawn_impact_sparks(self, x, y, direction_x, color=(56, 189, 248), count=8):
        for _ in range(count):
            angle_speed_x = direction_x * random.uniform(1.5, 5.0)
            speed_y = random.uniform(-3.5, 3.5)
            size = random.uniform(2, 4)
            lifespan = random.randint(10, 22)
            self.particles.append(Particle(x, y, angle_speed_x, speed_y, color, size, lifespan))

    def spawn_goal_explosion(self, x, y, color=(244, 63, 94), count=24):
        for _ in range(count):
            angle = random.uniform(0, 6.28318)
            speed = random.uniform(2.0, 8.0)
            vx = math_cos(angle) * speed
            vy = math_sin(angle) * speed
            size = random.uniform(2.5, 5)
            lifespan = random.randint(18, 35)
            self.particles.append(Particle(x, y, vx, vy, color, size, lifespan))

    def spawn_powerup_sparkles(self, x, y, color=(245, 158, 11), count=12):
        for _ in range(count):
            angle = random.uniform(0, 6.28318)
            speed = random.uniform(1.0, 4.0)
            vx = math_cos(angle) * speed
            vy = math_sin(angle) * speed
            size = random.uniform(2, 4)
            lifespan = random.randint(12, 25)
            self.particles.append(Particle(x, y, vx, vy, color, size, lifespan))

    def spawn_speed_trail(self, x, y, color=(56, 189, 248), count=2):
        for _ in range(count):
            vx = random.uniform(-0.8, 0.8)
            vy = random.uniform(-0.8, 0.8)
            size = random.uniform(1.5, 3.0)
            lifespan = random.randint(8, 16)
            self.particles.append(Particle(x, y, vx, vy, color, size, lifespan))

    def spawn_shockwave(self, x, y, color=(244, 63, 94), max_radius=40):
        p = Particle(x, y, 0, 0, color, 4, 20, shape="ring")
        p.growth = max_radius / 20.0
        self.particles.append(p)

def math_cos(rad):
    import math
    return math.cos(rad)

def math_sin(rad):
    import math
    return math.sin(rad)


