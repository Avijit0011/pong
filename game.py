import random
import pygame
from paddle import Paddle
from ball import Ball
from powerup import PowerUpManager
from particles import ParticleSystem
from audio import SoundEngine
from ui import UIRenderer, Button

class PongGame:
    def __init__(self, width=1000, height=600):
        self.width = width
        self.height = height
        
        # State: MENU, PLAYING, PAUSED, GAME_OVER
        self.state = "MENU"
        
        # Game Options
        self.mode = "VS_AI"  # VS_AI or TWO_PLAYER
        self.ai_difficulty = "Medium"
        self.target_score = 5
        self.powerups_enabled = True
        
        # Entities
        self.paddle1 = Paddle(40, height // 2, is_ai=False, color=(0, 245, 255), glow_color=(0, 180, 255))
        self.paddle2 = Paddle(width - 40, height // 2, is_ai=True, color=(255, 0, 128), glow_color=(255, 0, 180))
        self.paddle2.ai_difficulty = self.ai_difficulty
        
        self.balls = [Ball(width // 2, height // 2)]
        self.powerup_mgr = PowerUpManager()
        self.particle_sys = ParticleSystem()
        self.sound = SoundEngine()
        self.ui = UIRenderer(width, height)
        
        # Screen Shake effect
        self.shake_time = 0
        self.shake_magnitude = 0
        
        # Winner info
        self.winner_text = ""
        
        # Initialize Menu Buttons
        self._init_menu_buttons()

    def _init_menu_buttons(self):
        cx = self.width // 2
        btn_w = 260
        btn_h = 40
        
        self.btn_mode = Button(cx - btn_w // 2, 195, btn_w, btn_h, f"MODE: 1-PLAYER (AI)", self.ui.btn_font)
        self.btn_diff = Button(cx - btn_w // 2, 245, btn_w, btn_h, f"AI: {self.ai_difficulty.upper()}", self.ui.btn_font)
        self.btn_score = Button(cx - btn_w // 2, 295, btn_w, btn_h, f"TARGET SCORE: {self.target_score}", self.ui.btn_font)
        self.btn_power = Button(cx - btn_w // 2, 345, btn_w, btn_h, f"POWER-UPS: ON", self.ui.btn_font)
        
        self.btn_start = Button(cx - btn_w // 2, 405, btn_w, 46, "START MATCH 🚀", self.ui.btn_font, color=(0, 160, 90), hover_color=(0, 210, 120))
        self.btn_quit = Button(cx - btn_w // 2, 461, btn_w, 44, "QUIT GAME ❌", self.ui.btn_font, color=(160, 40, 40), hover_color=(210, 60, 60))
        
        # Pause Overlay buttons
        self.btn_pause_resume = Button(cx - 210, 310, 130, 46, "RESUME ▶️", self.ui.btn_font, color=(0, 150, 200), hover_color=(0, 190, 240))
        self.btn_pause_menu = Button(cx - 65, 310, 130, 46, "MENU 🏠", self.ui.btn_font)
        self.btn_pause_quit = Button(cx + 80, 310, 130, 46, "QUIT ❌", self.ui.btn_font, color=(160, 40, 40), hover_color=(210, 60, 60))

        # Game Over buttons
        self.btn_restart = Button(cx - 210, 330, 130, 48, "REPLAY 🔄", self.ui.btn_font)
        self.btn_go_menu = Button(cx - 65, 330, 130, 48, "MENU 🏠", self.ui.btn_font)
        self.btn_go_quit = Button(cx + 80, 330, 130, 48, "QUIT ❌", self.ui.btn_font, color=(160, 40, 40), hover_color=(210, 60, 60))

    def trigger_screen_shake(self, magnitude=12, duration=15):
        self.shake_magnitude = magnitude
        self.shake_time = duration

    def reset_match(self):
        self.paddle1.reset()
        self.paddle2.reset()
        self.paddle2.is_ai = (self.mode == "VS_AI")
        self.paddle2.ai_difficulty = self.ai_difficulty
        self.paddle1.score = 0
        self.paddle2.score = 0
        
        self.balls = [Ball(self.width // 2, self.height // 2)]
        self.powerup_mgr.reset()
        self.powerup_mgr.enabled = self.powerups_enabled
        self.particle_sys.particles.clear()
        self.shake_time = 0
        self.shake_magnitude = 0
        self.state = "PLAYING"

    def spawn_extra_ball(self, x, y, vx, vy):
        new_ball = Ball(x, y)
        new_ball.vx = -vx * 1.1
        new_ball.vy = -vy * 1.1
        new_ball.speed = math_sqrt(new_ball.vx**2 + new_ball.vy**2)
        self.balls.append(new_ball)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_ESCAPE, pygame.K_p]:
                if self.state == "PLAYING":
                    self.state = "PAUSED"
                elif self.state == "PAUSED":
                    self.state = "PLAYING"
            elif event.key == pygame.K_m:
                muted = self.sound.toggle_mute()
            elif event.key == pygame.K_r and self.state in ["PLAYING", "PAUSED", "GAME_OVER"]:
                self.reset_match()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            if self.state == "MENU":
                self.sound.play('click')
                if self.btn_mode.check_hover(mouse_pos):
                    if self.mode == "VS_AI":
                        self.mode = "TWO_PLAYER"
                        self.btn_mode.text = "MODE: 2-PLAYER LOCAL"
                    else:
                        self.mode = "VS_AI"
                        self.btn_mode.text = "MODE: 1-PLAYER (AI)"

                elif self.btn_diff.check_hover(mouse_pos):
                    diffs = ["Easy", "Medium", "Hard", "Impossible"]
                    idx = (diffs.index(self.ai_difficulty) + 1) % len(diffs)
                    self.ai_difficulty = diffs[idx]
                    self.btn_diff.text = f"AI: {self.ai_difficulty.upper()}"

                elif self.btn_score.check_hover(mouse_pos):
                    scores = [3, 5, 10, 15]
                    idx = (scores.index(self.target_score) + 1) % len(scores)
                    self.target_score = scores[idx]
                    self.btn_score.text = f"TARGET SCORE: {self.target_score}"

                elif self.btn_power.check_hover(mouse_pos):
                    self.powerups_enabled = not self.powerups_enabled
                    self.btn_power.text = f"POWER-UPS: {'ON' if self.powerups_enabled else 'OFF'}"

                elif self.btn_start.check_hover(mouse_pos):
                    self.reset_match()

                elif self.btn_quit.check_hover(mouse_pos):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

            elif self.state == "PAUSED":
                self.sound.play('click')
                if self.btn_pause_resume.check_hover(mouse_pos):
                    self.state = "PLAYING"
                elif self.btn_pause_menu.check_hover(mouse_pos):
                    self.state = "MENU"
                    self.shake_time = 0
                    self.shake_magnitude = 0
                    self.particle_sys.particles.clear()
                elif self.btn_pause_quit.check_hover(mouse_pos):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

            elif self.state == "GAME_OVER":
                self.sound.play('click')
                if self.btn_restart.check_hover(mouse_pos):
                    self.reset_match()
                elif self.btn_go_menu.check_hover(mouse_pos):
                    self.state = "MENU"
                    self.shake_time = 0
                    self.shake_magnitude = 0
                    self.particle_sys.particles.clear()
                elif self.btn_go_quit.check_hover(mouse_pos):
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self):
        # Always decay screen shake timer
        if self.shake_time > 0:
            self.shake_time -= 1

        mouse_pos = pygame.mouse.get_pos()
        
        if self.state == "MENU":
            self.btn_mode.check_hover(mouse_pos)
            self.btn_diff.check_hover(mouse_pos)
            self.btn_score.check_hover(mouse_pos)
            self.btn_power.check_hover(mouse_pos)
            self.btn_start.check_hover(mouse_pos)
            self.btn_quit.check_hover(mouse_pos)
            return

        if self.state == "PAUSED":
            self.btn_pause_resume.check_hover(mouse_pos)
            self.btn_pause_menu.check_hover(mouse_pos)
            self.btn_pause_quit.check_hover(mouse_pos)
            return

        if self.state == "GAME_OVER":
            self.btn_restart.check_hover(mouse_pos)
            self.btn_go_menu.check_hover(mouse_pos)
            self.btn_go_quit.check_hover(mouse_pos)
            self.particle_sys.update()
            return

        if self.state != "PLAYING":
            return

        # Update input keys
        keys = pygame.key.get_pressed()
        p1_up = keys[pygame.K_w]
        p1_dn = keys[pygame.K_s]
        p2_up = keys[pygame.K_UP]
        p2_dn = keys[pygame.K_DOWN]

        # Update Paddles
        self.paddle1.update(self.height, p1_up, p1_dn, balls=self.balls)
        self.paddle2.update(self.height, p2_up, p2_dn, balls=self.balls)

        # Update Balls
        for ball in self.balls[:]:
            ball.update(self.width, self.height, sound_engine=self.sound, particle_system=self.particle_sys)
            
            # Paddle collisions
            ball.check_paddle_collision(self.paddle1, sound_engine=self.sound, particle_system=self.particle_sys)
            ball.check_paddle_collision(self.paddle2, sound_engine=self.sound, particle_system=self.particle_sys)

            # Goal check (Left boundary score for Player 2, Right boundary score for Player 1)
            if ball.x <= -10:
                if self.paddle1.has_shield:
                    ball.vx = abs(ball.vx)
                    ball.x = 25
                    self.paddle1.has_shield = False
                    self.sound.play('wall_hit')
                else:
                    self._on_goal_scored(scorer=2, ball=ball)
                    if len(self.balls) > 1:
                        self.balls.remove(ball)
                    else:
                        ball.reset(direction=1)

            elif ball.x >= self.width + 10:
                if self.paddle2.has_shield:
                    ball.vx = -abs(ball.vx)
                    ball.x = self.width - 25
                    self.paddle2.has_shield = False
                    self.sound.play('wall_hit')
                else:
                    self._on_goal_scored(scorer=1, ball=ball)
                    if len(self.balls) > 1:
                        self.balls.remove(ball)
                    else:
                        ball.reset(direction=-1)

        # Update Powerups
        self.powerup_mgr.update(self.width, self.height, self.balls, self.paddle1, self.paddle2, self.sound, self.particle_sys, self.spawn_extra_ball)

        # Update Particles
        self.particle_sys.update()

    def _on_goal_scored(self, scorer, ball):
        if scorer == 1:
            self.paddle1.score += 1
            self.particle_sys.spawn_goal_explosion(self.width - 15, ball.y, color=(0, 245, 255), count=60)
        else:
            self.paddle2.score += 1
            self.particle_sys.spawn_goal_explosion(15, ball.y, color=(255, 0, 128), count=60)

        self.sound.play('score')
        self.trigger_screen_shake(16, 20)

        # Check match point victory
        if self.paddle1.score >= self.target_score:
            self.winner_text = "PLAYER 1 WINS!"
            self.state = "GAME_OVER"
            self.sound.play('victory')
        elif self.paddle2.score >= self.target_score:
            self.winner_text = "AI OVERLORD WINS!" if self.mode == "VS_AI" else "PLAYER 2 WINS!"
            self.state = "GAME_OVER"
            self.sound.play('victory')

    def draw(self, surface):
        # Calculate screen shake offset
        render_surf = surface
        shake_offset_x = 0
        shake_offset_y = 0
        if self.shake_time > 0:
            shake_offset_x = random.randint(-self.shake_magnitude, self.shake_magnitude)
            shake_offset_y = random.randint(-self.shake_magnitude, self.shake_magnitude)
            shake_surf = pygame.Surface((self.width, self.height))
            render_surf = shake_surf

        # Draw dark canvas background
        self.ui.draw_background(render_surf)

        if self.state == "MENU":
            self._draw_main_menu(render_surf)
        else:
            # Draw game elements
            p2_name = f"AI ({self.ai_difficulty.upper()})" if self.mode == "VS_AI" else "PLAYER 2"
            max_rally = max([b.rally_count for b in self.balls]) if self.balls else 0
            max_speed = max([b.speed for b in self.balls]) if self.balls else 9.0
            
            self.ui.draw_hud(render_surf, self.paddle1.score, self.paddle2.score, "PLAYER 1", p2_name, max_rally, max_speed, self.powerups_enabled, self.sound.muted)
            
            # Draw Powerups
            self.powerup_mgr.draw(render_surf, self.ui.hud_font)
            
            # Draw Paddles & Balls
            self.paddle1.draw(render_surf)
            self.paddle2.draw(render_surf)
            for b in self.balls:
                b.draw(render_surf)

            # Draw Particles
            self.particle_sys.draw(render_surf)

            # Overlays
            if self.state == "PAUSED":
                self.ui.draw_pause_overlay(render_surf)
                self.btn_pause_resume.draw(render_surf)
                self.btn_pause_menu.draw(render_surf)
                self.btn_pause_quit.draw(render_surf)
            elif self.state == "GAME_OVER":
                self.ui.draw_game_over(render_surf, self.winner_text)
                self.btn_restart.draw(render_surf)
                self.btn_go_menu.draw(render_surf)
                self.btn_go_quit.draw(render_surf)

        # Apply screen shake blit if active
        if self.shake_time > 0:
            surface.blit(render_surf, (shake_offset_x, shake_offset_y))

    def _draw_main_menu(self, surface):
        cx = self.width // 2
        
        # Animated neon glowing title
        t_surf = self.ui.title_font.render("NEON PONG 2D", True, (0, 245, 255))
        t_rect = t_surf.get_rect(center=(cx, 95))
        
        glow_t = self.ui.title_font.render("NEON PONG 2D", True, (0, 180, 255))
        surface.blit(glow_t, (t_rect.x - 3, t_rect.y - 3))
        surface.blit(t_surf, t_rect)

        sub_surf = self.ui.sub_font.render("RETRO DESKTOP ARCADE EDITION", True, (255, 0, 128))
        s_rect = sub_surf.get_rect(center=(cx, 150))
        surface.blit(sub_surf, s_rect)

        # Render menu buttons
        self.btn_mode.draw(surface)
        self.btn_diff.draw(surface)
        self.btn_score.draw(surface)
        self.btn_power.draw(surface)
        self.btn_start.draw(surface)
        self.btn_quit.draw(surface)

        # Controls legend bottom banner
        legend_txt = "CONTROLS: P1 [W / S]  |  P2 [UP / DOWN]  |  PAUSE [ESC / P]  |  MUTE [M]"
        l_surf = self.ui.hud_font.render(legend_txt, True, (130, 160, 190))
        l_rect = l_surf.get_rect(center=(cx, self.height - 25))
        surface.blit(l_surf, l_rect)

def math_sqrt(val):
    import math
    return math.sqrt(val)
