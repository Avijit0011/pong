import random
import pygame

class Paddle:
    def __init__(self, x, y, width=14, height=95, is_ai=False, color=(56, 189, 248), glow_color=(56, 189, 248)):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.base_width = width
        self.base_height = height
        self.width = width
        self.height = height
        self.color = color
        self.glow_color = glow_color
        self.is_ai = is_ai
        
        self.speed = 8.5
        self.vy = 0.0
        self.score = 0
        self.hit_flash = 0.0
        
        # Power-up status timers
        self.extend_timer = 0
        self.speed_boost_timer = 0
        self.has_shield = False
        
        # AI tuning attributes
        self.ai_difficulty = "Medium"  # Easy, Medium, Hard, Impossible
        self.ai_target_y = y
        self.ai_reaction_cooldown = 0
        self.ai_error_offset = 0

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.vy = 0.0
        self.width = self.base_width
        self.height = self.base_height
        self.extend_timer = 0
        self.speed_boost_timer = 0
        self.has_shield = False
        self.hit_flash = 0.0

    def get_rect(self):
        return pygame.Rect(int(self.x - self.width // 2), int(self.y - self.height // 2), self.width, self.height)

    def apply_powerup(self, p_type, duration=300):
        if p_type == "EXTEND":
            self.extend_timer = duration
            self.height = int(self.base_height * 1.5)
        elif p_type == "SPEED":
            self.speed_boost_timer = duration
        elif p_type == "SHIELD":
            self.has_shield = True

    def update(self, arena_height, up_pressed, down_pressed, balls=None):
        self.hit_flash *= 0.85

        # Update powerup timers
        if self.extend_timer > 0:
            self.extend_timer -= 1
            if self.extend_timer == 0:
                self.height = self.base_height
                
        effective_speed = self.speed * 1.4 if self.speed_boost_timer > 0 else self.speed
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= 1

        if self.is_ai:
            self._update_ai_logic(arena_height, balls, effective_speed)
        else:
            if up_pressed and not down_pressed:
                self.vy = -effective_speed
            elif down_pressed and not up_pressed:
                self.vy = effective_speed
            else:
                self.vy *= 0.4  # Smooth decelerating damping

        # Apply movement & arena boundaries constraint
        self.y += self.vy
        half_h = self.height / 2.0
        if self.y - half_h < 15:
            self.y = 15 + half_h
            self.vy = 0
        elif self.y + half_h > arena_height - 15:
            self.y = arena_height - 15 - half_h
            self.vy = 0

    def _update_ai_logic(self, arena_height, balls, speed):
        if not balls or len(balls) == 0:
            return

        # Target the primary ball or closest incoming ball
        target_ball = None
        closest_dist = 99999.0
        for b in balls:
            dist = abs(b.x - self.x)
            # Prioritize balls moving towards AI
            is_moving_towards = (b.vx > 0 and self.x > arena_height / 2) or (b.vx < 0 and self.x < arena_height / 2)
            if is_moving_towards and dist < closest_dist:
                closest_dist = dist
                target_ball = b
                
        if not target_ball:
            target_ball = balls[0]

        # AI decision parameters per difficulty
        if self.ai_difficulty == "Easy":
            reaction_delay = 8
            ai_max_speed = speed * 0.65
            error_range = 45
        elif self.ai_difficulty == "Medium":
            reaction_delay = 4
            ai_max_speed = speed * 0.88
            error_range = 25
        elif self.ai_difficulty == "Hard":
            reaction_delay = 2
            ai_max_speed = speed * 1.05
            error_range = 10
        else:  # Impossible
            reaction_delay = 0
            ai_max_speed = speed * 1.3
            error_range = 2

        self.ai_reaction_cooldown -= 1
        if self.ai_reaction_cooldown <= 0:
            self.ai_reaction_cooldown = reaction_delay
            # Calculate target Y (predict trajectory if ball moving towards AI)
            predicted_y = target_ball.y
            if self.ai_difficulty in ["Hard", "Impossible"] and target_ball.vx != 0:
                # Simple linear prediction with wall reflection calculation
                time_to_reach = abs(self.x - target_ball.x) / max(0.1, abs(target_ball.vx))
                future_y = target_ball.y + target_ball.vy * time_to_reach
                # Bounce math
                playable_h = arena_height - 30
                while future_y < 15 or future_y > arena_height - 15:
                    if future_y < 15:
                        future_y = 15 + (15 - future_y)
                    elif future_y > arena_height - 15:
                        future_y = (arena_height - 15) - (future_y - (arena_height - 15))
                predicted_y = future_y

            self.ai_error_offset = random.uniform(-error_range, error_range)
            self.ai_target_y = predicted_y + self.ai_error_offset

        # Move towards target Y smoothly
        dy = self.ai_target_y - self.y
        if abs(dy) > 5:
            move_dir = 1.0 if dy > 0 else -1.0
            self.vy = move_dir * min(abs(dy), ai_max_speed)
        else:
            self.vy *= 0.3

    def draw(self, surface):
        rect = self.get_rect()
        
        # Subtle ambient halo around paddle
        glow_size = 6
        glow_surf = pygame.Surface((rect.width + glow_size * 2, rect.height + glow_size * 2), pygame.SRCALPHA)
        glow_color_alpha = (self.glow_color[0], self.glow_color[1], self.glow_color[2], int(35 + 40 * self.hit_flash))
        pygame.draw.rect(glow_surf, glow_color_alpha, (0, 0, rect.width + glow_size * 2, rect.height + glow_size * 2), border_radius=6)
        surface.blit(glow_surf, (rect.x - glow_size, rect.y - glow_size))
        
        # Flash color blend
        r = int(self.color[0] + (255 - self.color[0]) * self.hit_flash * 0.6)
        g = int(self.color[1] + (255 - self.color[1]) * self.hit_flash * 0.6)
        b = int(self.color[2] + (255 - self.color[2]) * self.hit_flash * 0.6)
        cur_color = (min(255, r), min(255, g), min(255, b))

        # Main rounded paddle bar
        pygame.draw.rect(surface, cur_color, rect, border_radius=5)
        
        # Crisp edge outline
        pygame.draw.rect(surface, (255, 255, 255), rect, width=1, border_radius=5)
        
        # Shield wall indicator if active
        if self.has_shield:
            shield_x = rect.x - 12 if rect.x > surface.get_width() / 2 else rect.x + rect.width + 6
            shield_rect = pygame.Rect(shield_x, 16, 4, surface.get_height() - 32)
            pygame.draw.rect(surface, (52, 211, 153), shield_rect, border_radius=2)

