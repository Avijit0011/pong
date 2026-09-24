import random
import pygame
from paddle import Paddle
from ball import Ball
from powerup import PowerUpManager
from particles import ParticleSystem
from audio import SoundEngine
from ui import UIRenderer, Button, InputBox, ChatSystem
from network import NetworkServer, NetworkClient, get_local_ip

class PongGame:
    def __init__(self, width=1000, height=600):
        self.width = width
        self.height = height
        
        # State: MENU, LOBBY_HOST, LOBBY_JOIN, PLAYING, PAUSED, GAME_OVER
        self.state = "MENU"
        
        # Game Options: VS_AI, TWO_PLAYER, ONLINE_HOST, ONLINE_JOIN
        self.mode = "VS_AI"
        self.ai_difficulty = "Medium"
        self.target_score = 5
        self.powerups_enabled = True
        
        # Both-side Ready Flags
        self.p1_ready = True
        self.p2_ready = True
        
        # Networking & Chat
        self.local_ip = get_local_ip()
        self.host_port = 5555
        self.net_server = None
        self.net_client = None
        self.join_ip_box = InputBox(width // 2 - 130, 245, 260, 42, font=pygame.font.SysFont("Consolas", 20, bold=True), text="127.0.0.1")
        self.status_msg = ""
        self.status_color = (0, 245, 255)
        
        # Entities
        self.paddle1 = Paddle(40, height // 2, is_ai=False, color=(56, 189, 248), glow_color=(56, 189, 248))
        self.paddle2 = Paddle(width - 40, height // 2, is_ai=True, color=(244, 63, 94), glow_color=(244, 63, 94))
        self.paddle2.ai_difficulty = self.ai_difficulty
        
        self.balls = [Ball(width // 2, height // 2)]
        self.powerup_mgr = PowerUpManager()
        self.particle_sys = ParticleSystem()
        self.sound = SoundEngine()
        self.ui = UIRenderer(width, height)
        self.chat = ChatSystem(self.ui.hud_font)
        
        # Screen Shake effect
        self.shake_time = 0
        self.shake_magnitude = 0
        
        # Winner info
        self.winner_text = ""
        
        # Outgoing chat queues
        self.pending_outgoing_chat = []
        
        # Initialize Menu Buttons
        self._init_menu_buttons()

    def _init_menu_buttons(self):
        cx = self.width // 2
        btn_w = 280
        btn_h = 40
        
        self.btn_mode = Button(cx - btn_w // 2, 195, btn_w, btn_h, "MODE: 1-PLAYER (AI)", self.ui.btn_font)
        self.btn_diff = Button(cx - btn_w // 2, 245, btn_w, btn_h, f"AI DIFFICULTY: {self.ai_difficulty.upper()}", self.ui.btn_font)
        self.btn_score = Button(cx - btn_w // 2, 295, btn_w, btn_h, f"TARGET SCORE: {self.target_score}", self.ui.btn_font)
        self.btn_power = Button(cx - btn_w // 2, 345, btn_w, btn_h, "POWER-UPS: ON", self.ui.btn_font)
        
        self.btn_start = Button(cx - btn_w // 2, 405, btn_w, 44, "START MATCH", self.ui.btn_font, color=(56, 189, 248), hover_color=(14, 165, 233), text_color=(15, 23, 42))
        self.btn_quit = Button(cx - btn_w // 2, 459, btn_w, 42, "QUIT", self.ui.btn_font, color=(30, 41, 59), hover_color=(51, 65, 85), text_color=(244, 63, 94))
        
        # Lobby buttons
        self.btn_connect = Button(cx - 110, 305, 220, 42, "CONNECT", self.ui.btn_font, color=(56, 189, 248), hover_color=(14, 165, 233), text_color=(15, 23, 42))
        self.btn_lobby_cancel = Button(cx - 110, 360, 220, 40, "CANCEL", self.ui.btn_font, color=(30, 41, 59), hover_color=(51, 65, 85))

        # Ready Button
        self.btn_toggle_ready = Button(cx - 110, self.height // 2 + 10, 220, 44, "TOGGLE READY", self.ui.btn_font, color=(56, 189, 248), hover_color=(14, 165, 233), text_color=(15, 23, 42))

        # Pause Overlay buttons
        self.btn_pause_resume = Button(cx - 210, 310, 130, 44, "RESUME", self.ui.btn_font, color=(56, 189, 248), hover_color=(14, 165, 233), text_color=(15, 23, 42))
        self.btn_pause_menu = Button(cx - 65, 310, 130, 44, "MAIN MENU", self.ui.btn_font)
        self.btn_pause_quit = Button(cx + 80, 310, 130, 44, "QUIT", self.ui.btn_font, color=(30, 41, 59), hover_color=(51, 65, 85), text_color=(244, 63, 94))

        # Game Over buttons
        self.btn_restart = Button(cx - 210, 330, 130, 44, "PLAY AGAIN", self.ui.btn_font, color=(56, 189, 248), hover_color=(14, 165, 233), text_color=(15, 23, 42))
        self.btn_go_menu = Button(cx - 65, 330, 130, 44, "MAIN MENU", self.ui.btn_font)
        self.btn_go_quit = Button(cx + 80, 330, 130, 44, "QUIT", self.ui.btn_font, color=(30, 41, 59), hover_color=(51, 65, 85), text_color=(244, 63, 94))

    def trigger_screen_shake(self, magnitude=3, duration=8):
        self.shake_magnitude = magnitude
        self.shake_time = duration

    def reset_match(self):
        self.paddle1.reset()
        self.paddle2.reset()
        self.paddle2.is_ai = (self.mode == "VS_AI")
        self.paddle2.ai_difficulty = self.ai_difficulty
        self.paddle1.score = 0
        self.paddle2.score = 0
        
        # Reset Ready flags for online modes
        if self.mode in ["ONLINE_HOST", "ONLINE_JOIN"]:
            self.p1_ready = False
            self.p2_ready = False
        else:
            self.p1_ready = True
            self.p2_ready = True
        
        self.balls = [Ball(self.width // 2, self.height // 2)]
        self.powerup_mgr.reset()
        self.powerup_mgr.enabled = self.powerups_enabled
        self.particle_sys.particles.clear()
        self.shake_time = 0
        self.shake_magnitude = 0
        self.winner_text = ""
        self.state = "PLAYING"

    def spawn_extra_ball(self, x, y, vx, vy):
        new_ball = Ball(x, y)
        new_ball.vx = -vx * 1.1
        new_ball.vy = -vy * 1.1
        new_ball.speed = math_sqrt(new_ball.vx**2 + new_ball.vy**2)
        self.balls.append(new_ball)

    def handle_event(self, event):
        # Pass event to Chat System if in online mode
        if self.mode in ["ONLINE_HOST", "ONLINE_JOIN"] and self.state in ["PLAYING", "GAME_OVER"]:
            chat_sent = self.chat.handle_event(event)
            if chat_sent:
                sender_label = "P1" if self.mode == "ONLINE_HOST" else "P2"
                color = (0, 245, 255) if self.mode == "ONLINE_HOST" else (255, 0, 128)
                self.chat.add_message(sender_label, chat_sent, color=color)
                self.pending_outgoing_chat.append(f"[{sender_label}]: {chat_sent}")
                return

            if self.chat.active:
                return

        if self.mode == "ONLINE_JOIN" and self.state in ["MENU", "LOBBY_JOIN"]:
            self.join_ip_box.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_ESCAPE, pygame.K_p]:
                if self.state == "PLAYING":
                    self.state = "PAUSED"
                elif self.state == "PAUSED":
                    self.state = "PLAYING"
            elif event.key == pygame.K_m:
                self.sound.toggle_mute()
            elif event.key == pygame.K_SPACE and self.state == "PLAYING" and self.mode in ["ONLINE_HOST", "ONLINE_JOIN"]:
                self._toggle_local_ready()
            elif event.key == pygame.K_r and self.state in ["PLAYING", "PAUSED", "GAME_OVER"]:
                if self.mode not in ["ONLINE_HOST", "ONLINE_JOIN"]:
                    self.reset_match()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            
            if self.state == "PLAYING" and self.mode in ["ONLINE_HOST", "ONLINE_JOIN"]:
                if not (self.p1_ready and self.p2_ready):
                    if self.btn_toggle_ready.check_hover(mouse_pos):
                        self.sound.play('click')
                        self._toggle_local_ready()

            if self.state == "MENU":
                self.sound.play('click')
                if self.btn_mode.check_hover(mouse_pos):
                    modes = ["VS_AI", "TWO_PLAYER", "ONLINE_HOST", "ONLINE_JOIN"]
                    idx = (modes.index(self.mode) + 1) % len(modes)
                    self.mode = modes[idx]
                    
                    if self.mode == "VS_AI":
                        self.btn_mode.text = "MODE: 1-PLAYER (AI)"
                    elif self.mode == "TWO_PLAYER":
                        self.btn_mode.text = "MODE: 2-PLAYER LOCAL"
                    elif self.mode == "ONLINE_HOST":
                        self.btn_mode.text = "MODE: ONLINE HOST"
                    elif self.mode == "ONLINE_JOIN":
                        self.btn_mode.text = "MODE: ONLINE JOIN"

                elif self.btn_diff.check_hover(mouse_pos) and self.mode == "VS_AI":
                    diffs = ["Easy", "Medium", "Hard", "Impossible"]
                    idx = (diffs.index(self.ai_difficulty) + 1) % len(diffs)
                    self.ai_difficulty = diffs[idx]
                    self.btn_diff.text = f"AI DIFFICULTY: {self.ai_difficulty.upper()}"

                elif self.btn_score.check_hover(mouse_pos):
                    scores = [3, 5, 10, 15]
                    idx = (scores.index(self.target_score) + 1) % len(scores)
                    self.target_score = scores[idx]
                    self.btn_score.text = f"TARGET SCORE: {self.target_score}"

                elif self.btn_power.check_hover(mouse_pos):
                    self.powerups_enabled = not self.powerups_enabled
                    self.btn_power.text = f"POWER-UPS: {'ON' if self.powerups_enabled else 'OFF'}"

                elif self.btn_start.check_hover(mouse_pos):
                    if self.mode in ["VS_AI", "TWO_PLAYER"]:
                        self.reset_match()
                    elif self.mode == "ONLINE_HOST":
                        self._start_host_lobby()
                    elif self.mode == "ONLINE_JOIN":
                        self.state = "LOBBY_JOIN"
                        self.status_msg = "Enter Host IP address and click Connect"
                        self.status_color = (200, 220, 240)

                elif self.btn_quit.check_hover(mouse_pos):
                    self._cleanup_network()
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

            elif self.state == "LOBBY_HOST":
                self.sound.play('click')
                if self.btn_lobby_cancel.check_hover(mouse_pos):
                    self._cleanup_network()
                    self.state = "MENU"

            elif self.state == "LOBBY_JOIN":
                self.sound.play('click')
                if self.btn_connect.check_hover(mouse_pos):
                    self._attempt_join_connect()
                elif self.btn_lobby_cancel.check_hover(mouse_pos):
                    self._cleanup_network()
                    self.state = "MENU"

            elif self.state == "PAUSED":
                self.sound.play('click')
                if self.btn_pause_resume.check_hover(mouse_pos):
                    self.state = "PLAYING"
                elif self.btn_pause_menu.check_hover(mouse_pos):
                    self._cleanup_network()
                    self.state = "MENU"
                    self.shake_time = 0
                    self.shake_magnitude = 0
                    self.particle_sys.particles.clear()
                elif self.btn_pause_quit.check_hover(mouse_pos):
                    self._cleanup_network()
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

            elif self.state == "GAME_OVER":
                self.sound.play('click')
                if self.btn_restart.check_hover(mouse_pos):
                    self.reset_match()
                elif self.btn_go_menu.check_hover(mouse_pos):
                    self._cleanup_network()
                    self.state = "MENU"
                    self.shake_time = 0
                    self.shake_magnitude = 0
                    self.particle_sys.particles.clear()
                elif self.btn_go_quit.check_hover(mouse_pos):
                    self._cleanup_network()
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _toggle_local_ready(self):
        if self.mode == "ONLINE_HOST":
            self.p1_ready = not self.p1_ready
        elif self.mode == "ONLINE_JOIN":
            self.p2_ready = not self.p2_ready

    def _start_host_lobby(self):
        self._cleanup_network()
        self.net_server = NetworkServer(port=self.host_port)
        ok, msg = self.net_server.start()
        if ok:
            self.state = "LOBBY_HOST"
            self.status_msg = f"WAITING FOR PLAYER 2... (IP: {self.local_ip}:{self.host_port})"
            self.status_color = (0, 245, 255)
        else:
            self.status_msg = f"ERROR: {msg}"
            self.status_color = (255, 60, 60)

    def _attempt_join_connect(self):
        self._cleanup_network()
        target_ip = self.join_ip_box.text.strip()
        self.status_msg = f"Connecting to {target_ip}:{self.host_port}..."
        self.status_color = (255, 200, 0)
        
        self.net_client = NetworkClient()
        ok, msg = self.net_client.connect(target_ip, self.host_port)
        if ok:
            self.paddle1.is_ai = False
            self.paddle2.is_ai = False
            self.reset_match()
            self.sound.play('click')
        else:
            self.status_msg = f"Failed to connect to {target_ip}"
            self.status_color = (255, 60, 60)

    def _cleanup_network(self):
        if self.net_server:
            self.net_server.stop()
            self.net_server = None
        if self.net_client:
            self.net_client.disconnect()
            self.net_client = None

    def update(self):
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

        if self.state == "LOBBY_HOST":
            self.btn_lobby_cancel.check_hover(mouse_pos)
            if self.net_server and self.net_server.is_connected:
                self.reset_match()
            return

        if self.state == "LOBBY_JOIN":
            self.btn_connect.check_hover(mouse_pos)
            self.btn_lobby_cancel.check_hover(mouse_pos)
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

        # Check Ready button hover if in pre-match
        if self.mode in ["ONLINE_HOST", "ONLINE_JOIN"] and not (self.p1_ready and self.p2_ready):
            self.btn_toggle_ready.check_hover(mouse_pos)

        # -------------------------------------------------------------------
        # ONLINE JOINER UPDATE
        # -------------------------------------------------------------------
        if self.mode == "ONLINE_JOIN":
            if not self.net_client or not self.net_client.is_connected:
                self.state = "MENU"
                self.status_msg = "DISCONNECTED FROM HOST"
                return

            keys = pygame.key.get_pressed()
            p2_up = False
            p2_dn = False
            if not self.chat.active:
                p2_up = keys[pygame.K_UP] or keys[pygame.K_w]
                p2_dn = keys[pygame.K_DOWN] or keys[pygame.K_s]
            
            # Send input & ready status to Host
            chat_to_send = self.pending_outgoing_chat.pop(0) if self.pending_outgoing_chat else ""
            self.net_client.send_input({
                "up": p2_up,
                "down": p2_dn,
                "ready": self.p2_ready,
                "chat_msg": chat_to_send
            })
            
            # Read incoming chat from host
            inc_chat = self.net_client.pop_incoming_chat()
            for msg_str in inc_chat:
                if msg_str.startswith("[P1]: "):
                    self.chat.add_message("P1", msg_str[6:], color=(0, 245, 255))

            # Receive Host State Snapshot
            remote_state = self.net_client.get_game_state()
            if remote_state:
                self._apply_remote_state(remote_state)

            self.particle_sys.update()
            return

        # -------------------------------------------------------------------
        # HOST / LOCAL MASTER UPDATE
        # -------------------------------------------------------------------
        keys = pygame.key.get_pressed()
        p1_up = False
        p1_dn = False
        if not self.chat.active:
            p1_up = keys[pygame.K_w]
            p1_dn = keys[pygame.K_s]
        
        p2_up = False
        p2_dn = False

        if self.mode == "TWO_PLAYER":
            p2_up = keys[pygame.K_UP]
            p2_dn = keys[pygame.K_DOWN]
        elif self.mode == "ONLINE_HOST":
            if not self.net_server or not self.net_server.is_connected:
                self.state = "MENU"
                self.status_msg = "CLIENT DISCONNECTED"
                return
            client_input = self.net_server.get_client_input()
            p2_up = client_input.get("up", False)
            p2_dn = client_input.get("down", False)
            self.p2_ready = client_input.get("ready", False)

            # Read incoming chat from joiner
            inc_chat = self.net_server.pop_incoming_chat()
            for msg_str in inc_chat:
                if msg_str.startswith("[P2]: "):
                    self.chat.add_message("P2", msg_str[6:], color=(255, 0, 128))

        # Update Paddles (Paddles can move even in pre-match ready phase)
        self.paddle1.update(self.height, p1_up, p1_dn, balls=self.balls)
        self.paddle2.update(self.height, p2_up, p2_dn, balls=self.balls)

        # Check if ball physics should advance (requires BOTH players ready in Online mode)
        both_ready = (self.mode not in ["ONLINE_HOST", "ONLINE_JOIN"]) or (self.p1_ready and self.p2_ready)
        
        if both_ready:
            # Update Balls
            for ball in self.balls[:]:
                ball.update(self.width, self.height, sound_engine=self.sound, particle_system=self.particle_sys)
                
                # Paddle collisions
                ball.check_paddle_collision(self.paddle1, sound_engine=self.sound, particle_system=self.particle_sys)
                ball.check_paddle_collision(self.paddle2, sound_engine=self.sound, particle_system=self.particle_sys)

                # Goal check
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

        # Broadcast state if ONLINE_HOST
        if self.mode == "ONLINE_HOST" and self.net_server:
            chat_to_send = self.pending_outgoing_chat.pop(0) if self.pending_outgoing_chat else ""
            serialized = self._serialize_state()
            if chat_to_send:
                serialized["chat_broadcast"] = [chat_to_send]
            self.net_server.broadcast_state(serialized)

    def _serialize_state(self):
        return {
            "state": self.state,
            "winner_text": self.winner_text,
            "p1_ready": self.p1_ready,
            "p2_ready": self.p2_ready,
            "p1_y": self.paddle1.y,
            "p1_h": self.paddle1.height,
            "p1_s": self.paddle1.score,
            "p1_sh": self.paddle1.has_shield,
            "p2_y": self.paddle2.y,
            "p2_h": self.paddle2.height,
            "p2_s": self.paddle2.score,
            "p2_sh": self.paddle2.has_shield,
            "balls": [{"x": b.x, "y": b.y, "vx": b.vx, "vy": b.vy, "s": b.speed, "r": b.rally_count} for b in self.balls],
            "powerups": [{"type": p.type, "x": p.x, "y": p.y} for p in self.powerup_mgr.active_powerups]
        }

    def _apply_remote_state(self, data):
        if not data:
            return
        self.p1_ready = data.get("p1_ready", False)
        self.p2_ready = data.get("p2_ready", False)

        self.paddle1.y = data.get("p1_y", self.paddle1.y)
        self.paddle1.height = data.get("p1_h", self.paddle1.height)
        self.paddle1.score = data.get("p1_s", self.paddle1.score)
        self.paddle1.has_shield = data.get("p1_sh", False)

        self.paddle2.y = data.get("p2_y", self.paddle2.y)
        self.paddle2.height = data.get("p2_h", self.paddle2.height)
        self.paddle2.score = data.get("p2_s", self.paddle2.score)
        self.paddle2.has_shield = data.get("p2_sh", False)

        balls_data = data.get("balls", [])
        if balls_data:
            while len(self.balls) < len(balls_data):
                self.balls.append(Ball(self.width // 2, self.height // 2))
            while len(self.balls) > len(balls_data):
                self.balls.pop()

            for i, b_data in enumerate(balls_data):
                self.balls[i].x = b_data["x"]
                self.balls[i].y = b_data["y"]
                self.balls[i].vx = b_data["vx"]
                self.balls[i].vy = b_data["vy"]
                self.balls[i].speed = b_data.get("s", 9.0)
                self.balls[i].rally_count = b_data.get("r", 0)

        self.winner_text = data.get("winner_text", "")
        remote_state = data.get("state", "PLAYING")
        if remote_state in ["PLAYING", "GAME_OVER", "PAUSED"]:
            self.state = remote_state

    def _on_goal_scored(self, scorer, ball):
        if scorer == 1:
            self.paddle1.score += 1
            self.particle_sys.spawn_goal_explosion(self.width - 15, ball.y, color=(56, 189, 248), count=24)
        else:
            self.paddle2.score += 1
            self.particle_sys.spawn_goal_explosion(15, ball.y, color=(244, 63, 94), count=24)

        self.sound.play('score')
        self.trigger_screen_shake(4, 10)

        if self.paddle1.score >= self.target_score:
            self.winner_text = "PLAYER 1 WINS!"
            self.state = "GAME_OVER"
            self.sound.play('victory')
        elif self.paddle2.score >= self.target_score:
            self.winner_text = "PLAYER 2 WINS!" if self.mode != "VS_AI" else "AI WINS!"
            self.state = "GAME_OVER"
            self.sound.play('victory')

    def draw(self, surface):
        render_surf = surface
        shake_offset_x = 0
        shake_offset_y = 0
        if self.shake_time > 0:
            shake_offset_x = random.randint(-self.shake_magnitude, self.shake_magnitude)
            shake_offset_y = random.randint(-self.shake_magnitude, self.shake_magnitude)
            shake_surf = pygame.Surface((self.width, self.height))
            render_surf = shake_surf

        self.ui.draw_background(render_surf)

        if self.state == "MENU":
            self._draw_main_menu(render_surf)
        elif self.state == "LOBBY_HOST":
            self._draw_host_lobby(render_surf)
        elif self.state == "LOBBY_JOIN":
            self._draw_join_lobby(render_surf)
        else:
            p2_name = "PLAYER 2"
            if self.mode == "VS_AI":
                p2_name = f"AI ({self.ai_difficulty.upper()})"
            elif self.mode == "ONLINE_HOST":
                p2_name = "ONLINE GUEST"
            elif self.mode == "ONLINE_JOIN":
                p2_name = "ONLINE HOST"
                
            max_rally = max([b.rally_count for b in self.balls]) if self.balls else 0
            max_speed = max([b.speed for b in self.balls]) if self.balls else 9.0
            
            self.ui.draw_hud(render_surf, self.paddle1.score, self.paddle2.score, "PLAYER 1", p2_name, max_rally, max_speed, self.powerups_enabled, self.sound.muted)
            
            self.powerup_mgr.draw(render_surf, self.ui.hud_font)
            
            self.paddle1.draw(render_surf)
            self.paddle2.draw(render_surf)
            for b in self.balls:
                b.draw(render_surf)

            self.particle_sys.draw(render_surf)

            # Ready Confirmation Overlay if online match not ready
            if self.mode in ["ONLINE_HOST", "ONLINE_JOIN"] and self.state == "PLAYING" and not (self.p1_ready and self.p2_ready):
                p1_is_local = (self.mode == "ONLINE_HOST")
                self.ui.draw_ready_overlay(render_surf, self.p1_ready, self.p2_ready, p1_is_local)
                self.btn_toggle_ready.draw(render_surf)

            # Draw Chat system in Online mode
            if self.mode in ["ONLINE_HOST", "ONLINE_JOIN"]:
                self.chat.draw(render_surf, self.height)

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

        if self.shake_time > 0:
            surface.blit(render_surf, (shake_offset_x, shake_offset_y))

    def _draw_main_menu(self, surface):
        cx = self.width // 2
        
        t_surf = self.ui.title_font.render("PONG 2D", True, (241, 245, 249))
        t_rect = t_surf.get_rect(center=(cx, 95))
        surface.blit(t_surf, t_rect)

        sub_surf = self.ui.sub_font.render("MINIMALIST ARCADE", True, (148, 163, 184))
        s_rect = sub_surf.get_rect(center=(cx, 145))
        surface.blit(sub_surf, s_rect)

        self.btn_mode.draw(surface)
        if self.mode == "VS_AI":
            self.btn_diff.draw(surface)
        self.btn_score.draw(surface)
        self.btn_power.draw(surface)
        self.btn_start.draw(surface)
        self.btn_quit.draw(surface)

        if self.status_msg:
            st_surf = self.ui.hud_font.render(self.status_msg, True, self.status_color)
            surface.blit(st_surf, (cx - st_surf.get_width() // 2, 445))

        legend_txt = "CONTROLS: P1 [W / S]   |   P2 [UP / DOWN]   |   PAUSE [ESC / P]   |   MUTE [M]"
        l_surf = self.ui.hud_font.render(legend_txt, True, (100, 116, 139))
        l_rect = l_surf.get_rect(center=(cx, self.height - 25))
        surface.blit(l_surf, l_rect)

    def _draw_host_lobby(self, surface):
        cx = self.width // 2
        
        t_surf = self.ui.title_font.render("ONLINE LOBBY", True, (241, 245, 249))
        surface.blit(t_surf, t_surf.get_rect(center=(cx, 130)))

        ip_lbl = self.ui.sub_font.render(f"YOUR LOCAL IP: {self.local_ip}", True, (56, 189, 248))
        surface.blit(ip_lbl, ip_lbl.get_rect(center=(cx, 210)))

        port_lbl = self.ui.sub_font.render(f"PORT: {self.host_port}", True, (148, 163, 184))
        surface.blit(port_lbl, port_lbl.get_rect(center=(cx, 250)))

        dots = "." * ((pygame.time.get_ticks() // 400) % 4)
        st_surf = self.ui.sub_font.render(f"Waiting for Player 2 to join{dots}", True, (241, 245, 249))
        surface.blit(st_surf, st_surf.get_rect(center=(cx, 310)))

        self.btn_lobby_cancel.draw(surface)

    def _draw_join_lobby(self, surface):
        cx = self.width // 2
        
        t_surf = self.ui.title_font.render("JOIN ONLINE MATCH", True, (241, 245, 249))
        surface.blit(t_surf, t_surf.get_rect(center=(cx, 130)))

        ip_lbl = self.ui.sub_font.render("ENTER HOST IP ADDRESS:", True, (148, 163, 184))
        surface.blit(ip_lbl, ip_lbl.get_rect(center=(cx, 205)))

        self.join_ip_box.draw(surface)
        self.btn_connect.draw(surface)
        self.btn_lobby_cancel.draw(surface)

        if self.status_msg:
            st_surf = self.ui.hud_font.render(self.status_msg, True, self.status_color)
            surface.blit(st_surf, st_surf.get_rect(center=(cx, 420)))

def math_sqrt(val):
    import math
    return math.sqrt(val)
