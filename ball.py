import math
import random
import pygame

class Ball:
    def __init__(self, x, y, radius=9, color=(241, 245, 249), glow_color=(148, 163, 184)):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.glow_color = glow_color
        
        self.base_speed = 8.5
        self.max_speed = 20.0
        self.speed = self.base_speed
        self.vx = 0.0
        self.vy = 0.0
        
        self.trail = []  # List of previous positions (x, y)
        self.max_trail_len = 8
        self.rally_count = 0
        
        self.reset(direction=random.choice([-1, 1]))

    def reset(self, direction=1):
        self.x = self.start_x
        self.y = self.start_y
        self.speed = self.base_speed
        
        # Launch angle between -35 deg and +35 deg
        angle = math.radians(random.uniform(-35, 35))
        self.vx = direction * self.speed * math.cos(angle)
        self.vy = self.speed * math.sin(angle)
        self.trail.clear()
        self.rally_count = 0

    def update(self, arena_width, arena_height, sound_engine=None, particle_system=None):
        # Store current position in trail
        self.trail.insert(0, (self.x, self.y))
        if len(self.trail) > self.max_trail_len:
            self.trail.pop()

        # Update coordinates
        self.x += self.vx
        self.y += self.vy

        # Wall collisions (Top and Bottom boundaries)
        top_bound = 15 + self.radius
        bottom_bound = arena_height - 15 - self.radius

        if self.y <= top_bound:
            self.y = top_bound
            self.vy = abs(self.vy)
            if sound_engine:
                sound_engine.play('wall_hit')
            if particle_system:
                particle_system.spawn_impact_sparks(self.x, self.y, 0, color=(241, 245, 249), count=6)

        elif self.y >= bottom_bound:
            self.y = bottom_bound
            self.vy = -abs(self.vy)
            if sound_engine:
                sound_engine.play('wall_hit')
            if particle_system:
                particle_system.spawn_impact_sparks(self.x, self.y, 0, color=(241, 245, 249), count=6)

    def check_paddle_collision(self, paddle, sound_engine=None, particle_system=None):
        paddle_rect = paddle.get_rect()
        
        # Circle - Rectangle collision detection
        closest_x = max(paddle_rect.left, min(self.x, paddle_rect.right))
        closest_y = max(paddle_rect.top, min(self.y, paddle_rect.bottom))
        
        dist_x = self.x - closest_x
        dist_y = self.y - closest_y
        distance_sq = dist_x * dist_x + dist_y * dist_y
        
        if distance_sq < (self.radius * self.radius):
            # Collision occurred!
            self.rally_count += 1
            
            # Increase ball speed slightly each hit up to cap
            self.speed = min(self.max_speed, self.speed + 0.5)
            
            # Calculate hit position relative to paddle center (-1.0 at top to +1.0 at bottom)
            relative_intersect_y = (self.y - paddle.y) / (paddle.height / 2.0)
            relative_intersect_y = max(-1.0, min(1.0, relative_intersect_y))
            
            # Max bounce angle: 55 degrees
            max_bounce_angle = math.radians(55)
            bounce_angle = relative_intersect_y * max_bounce_angle
            
            # Direction facing towards center of court
            direction = 1.0 if paddle.x < self.start_x else -1.0
            
            # Apply velocity vector with spin effect from paddle motion
            self.vx = direction * self.speed * math.cos(bounce_angle)
            self.vy = self.speed * math.sin(bounce_angle) + (paddle.vy * 0.25)
            
            # Reposition outside paddle bounding box to prevent sticking
            if direction > 0:
                self.x = paddle_rect.right + self.radius + 1
            else:
                self.x = paddle_rect.left - self.radius - 1
                
            if sound_engine:
                sound_engine.play('paddle_hit')
            if particle_system:
                sparks_color = paddle.color
                particle_system.spawn_impact_sparks(self.x, self.y, direction, color=sparks_color, count=8)
            
            return True
        return False

    def draw(self, surface):
        # Draw smooth tapered trail
        for idx, (tx, ty) in enumerate(self.trail):
            ratio = 1.0 - (idx / len(self.trail))
            t_radius = max(2, int(self.radius * ratio * 0.75))
            alpha = int(100 * ratio)
            
            trail_surf = pygame.Surface((t_radius * 2, t_radius * 2), pygame.SRCALPHA)
            t_color = (self.glow_color[0], self.glow_color[1], self.glow_color[2], alpha)
            pygame.draw.circle(trail_surf, t_color, (t_radius, t_radius), t_radius)
            surface.blit(trail_surf, (tx - t_radius, ty - t_radius))

        # Soft subtle ambient halo
        glow_r = self.radius + 5
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 255, 255, 30), (glow_r, glow_r), glow_r)
        surface.blit(glow_surf, (self.x - glow_r, self.y - glow_r))

        # Main clean solid ball
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

