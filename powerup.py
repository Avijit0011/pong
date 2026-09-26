import math
import random
import pygame

POWERUP_TYPES = {
    "SPEED": {"color": (239, 68, 68), "glow": (239, 68, 68), "label": "S"},
    "SHIELD": {"color": (16, 185, 129), "glow": (16, 185, 129), "label": "W"},
    "EXTEND": {"color": (245, 158, 11), "glow": (245, 158, 11), "label": "E"},
    "MULTIBALL": {"color": (99, 102, 241), "glow": (99, 102, 241), "label": "M"},
    "SLOW_MO": {"color": (6, 182, 212), "glow": (6, 182, 212), "label": "T"}
}

class PowerUp:
    def __init__(self, x, y, p_type):
        self.x = x
        self.y = y
        self.radius = 15
        self.type = p_type
        self.info = POWERUP_TYPES[p_type]
        self.lifespan = 480  # 8 seconds at 60fps
        self.pulse_time = 0.0

    def update(self):
        self.lifespan -= 1
        self.pulse_time += 0.05

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def draw(self, surface, font):
        if self.lifespan <= 0:
            return
            
        pulse_scale = 1.0 + 0.08 * math.sin(self.pulse_time)
        cur_radius = int(self.radius * pulse_scale)
        
        # Soft ambient glow
        glow_r = cur_radius + 6
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        gc = self.info["glow"]
        pygame.draw.circle(glow_surf, (gc[0], gc[1], gc[2], 30), (glow_r, glow_r), glow_r)
        surface.blit(glow_surf, (self.x - glow_r, self.y - glow_r))
        
        # Main core shape
        pygame.draw.circle(surface, self.info["color"], (int(self.x), int(self.y)), cur_radius)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), cur_radius, width=1)
        
        # Label letter
        txt_surf = font.render(self.info["label"], True, (255, 255, 255))
        txt_rect = txt_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(txt_surf, txt_rect)

class PowerUpManager:
    def __init__(self):
        self.powerups = []
        self.spawn_timer = 0
        self.spawn_interval = random.randint(450, 750)  # 7.5 to 12.5 seconds
        self.enabled = True

    def reset(self):
        self.powerups.clear()
        self.spawn_timer = 0
        self.spawn_interval = random.randint(450, 750)

    def update(self, arena_width, arena_height, balls, paddle1, paddle2, sound_engine, particle_system, extra_ball_callback):
        if not self.enabled:
            return

        # Handle spawning timer
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval and len(self.powerups) < 2:
            self.spawn_timer = 0
            self.spawn_interval = random.randint(500, 900)
            
            # Spawn in central playing field zone
            spawn_x = random.randint(int(arena_width * 0.25), int(arena_width * 0.75))
            spawn_y = random.randint(80, arena_height - 80)
            p_type = random.choice(list(POWERUP_TYPES.keys()))
            self.powerups.append(PowerUp(spawn_x, spawn_y, p_type))
            if sound_engine:
                sound_engine.play('powerup_spawn')

        # Update powerups and check ball collision
        for p in self.powerups[:]:
            p.update()
            if p.lifespan <= 0:
                self.powerups.remove(p)
                continue

            # Check collision with any ball
            p_rect = p.get_rect()
            for ball in balls:
                b_rect = pygame.Rect(ball.x - ball.radius, ball.y - ball.radius, ball.radius * 2, ball.radius * 2)
                if p_rect.colliderect(b_rect):
                    # Powerup hit by ball! Determine beneficiary paddle based on ball direction
                    beneficiary = paddle1 if ball.vx > 0 else paddle2
                    
                    if p.type == "MULTIBALL":
                        extra_ball_callback(ball.x, ball.y, ball.vx, ball.vy)
                    elif p.type == "SPEED":
                        ball.speed = min(ball.max_speed, ball.speed * 1.5)
                        ball.vx *= 1.3
                        ball.vy *= 1.3
                    elif p.type == "SLOW_MO":
                        ball.speed = max(4.5, ball.speed * 0.6)
                        ball.vx *= 0.6
                        ball.vy *= 0.6
                    else:
                        beneficiary.apply_powerup(p.type)
                        
                    sound_engine.play('powerup')
                    particle_system.spawn_powerup_sparkles(p.x, p.y, color=p.info["color"], count=12)
                    self.powerups.remove(p)
                    break

    def draw(self, surface, font):
        if not self.enabled:
            return
        for p in self.powerups:
            p.draw(surface, font)

