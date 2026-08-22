import pygame
import time

class Button:
    def __init__(self, x, y, width, height, text, font, color=(30, 40, 60), hover_color=(0, 180, 255), text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered

    def draw(self, surface):
        bg_col = self.hover_color if self.is_hovered else self.color
        border_col = (0, 245, 255) if self.is_hovered else (80, 120, 160)
        
        # Outer glow if hovered
        if self.is_hovered:
            glow_surf = pygame.Surface((self.rect.width + 12, self.rect.height + 12), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (0, 245, 255, 80), (0, 0, self.rect.width + 12, self.rect.height + 12), border_radius=10)
            surface.blit(glow_surf, (self.rect.x - 6, self.rect.y - 6))

        # Main button body
        pygame.draw.rect(surface, bg_col, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_col, self.rect, width=2, border_radius=8)
        
        # Text label
        txt_surf = self.font.render(self.text, True, self.text_color)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)


class InputBox:
    def __init__(self, x, y, width, height, font, text='127.0.0.1'):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.text = text
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key not in [pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE, pygame.K_TAB]:
                if len(self.text) < 25 and (event.unicode.isprintable()):
                    self.text += event.unicode

    def draw(self, surface):
        bg_col = (20, 30, 50) if not self.active else (30, 45, 75)
        border_col = (0, 245, 255) if self.active else (100, 130, 160)
        
        pygame.draw.rect(surface, bg_col, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_col, self.rect, width=2, border_radius=8)
        
        display_text = self.text + ("|" if self.active and (pygame.time.get_ticks() // 500) % 2 == 0 else "")
        txt_surf = self.font.render(display_text, True, (255, 255, 255))
        surface.blit(txt_surf, (self.rect.x + 15, self.rect.y + (self.rect.height - txt_surf.get_height()) // 2))


class ChatSystem:
    def __init__(self, font):
        self.font = font
        self.messages = []  # list of {"sender": "P1", "text": "...", "time": timestamp, "color": tuple}
        self.active = False
        self.input_text = ""

    def add_message(self, sender, text, color=(0, 245, 255)):
        self.messages.append({
            "sender": sender,
            "text": text,
            "time": time.time(),
            "color": color
        })
        if len(self.messages) > 30:
            self.messages.pop(0)

    def handle_event(self, event):
        if not self.active:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_t, pygame.K_RETURN]:
                    self.active = True
                    self.input_text = ""
                    return None
            return None

        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                sent = self.input_text.strip()
                self.input_text = ""
                self.active = False
                return sent
            elif event.key == pygame.K_ESCAPE:
                self.input_text = ""
                self.active = False
                return None
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                if len(self.input_text) < 45 and event.unicode.isprintable():
                    self.input_text += event.unicode
        return None

    def draw(self, surface, screen_height):
        # Render recent chat log (last 5 messages)
        now = time.time()
        start_y = screen_height - 170
        
        # Background container for chat
        chat_box = pygame.Surface((340, 110), pygame.SRCALPHA)
        chat_box.fill((10, 15, 30, 160))
        pygame.draw.rect(chat_box, (0, 180, 255, 100), (0, 0, 340, 110), width=1, border_radius=6)
        surface.blit(chat_box, (15, start_y))

        recent_msgs = [m for m in self.messages if now - m["time"] < 12.0 or self.active][-5:]
        line_y = start_y + 8
        for msg in recent_msgs:
            prefix_color = msg["color"]
            sender_surf = self.font.render(f"[{msg['sender']}]: ", True, prefix_color)
            txt_surf = self.font.render(msg["text"], True, (240, 240, 240))
            
            surface.blit(sender_surf, (22, line_y))
            surface.blit(txt_surf, (22 + sender_surf.get_width(), line_y))
            line_y += 20

        # Render Active Input Box if typing
        if self.active:
            inp_box_surf = pygame.Surface((340, 32), pygame.SRCALPHA)
            inp_box_surf.fill((20, 35, 60, 220))
            pygame.draw.rect(inp_box_surf, (0, 245, 255), (0, 0, 340, 32), width=2, border_radius=6)
            surface.blit(inp_box_surf, (15, screen_height - 52))

            prompt = f"CHAT: {self.input_text}" + ("|" if (pygame.time.get_ticks() // 400) % 2 == 0 else "")
            p_surf = self.font.render(prompt, True, (0, 245, 255))
            surface.blit(p_surf, (25, screen_height - 45))
        else:
            hint_surf = self.font.render("Press [T] or [ENTER] to Chat", True, (100, 130, 170))
            surface.blit(hint_surf, (22, screen_height - 52))


class UIRenderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Initialize default fonts safely
        pygame.font.init()
        self.title_font = pygame.font.SysFont("Impact", 64) or pygame.font.Font(None, 72)
        self.sub_font = pygame.font.SysFont("Arial", 28, bold=True) or pygame.font.Font(None, 32)
        self.score_font = pygame.font.SysFont("Consolas", 52, bold=True) or pygame.font.Font(None, 56)
        self.hud_font = pygame.font.SysFont("Consolas", 18, bold=True) or pygame.font.Font(None, 20)
        self.btn_font = pygame.font.SysFont("Arial", 22, bold=True) or pygame.font.Font(None, 24)

    def draw_background(self, surface):
        surface.fill((10, 14, 26))
        grid_color = (20, 30, 50)
        for y in range(0, self.height, 40):
            pygame.draw.line(surface, grid_color, (0, y), (self.width, y), 1)

    def draw_center_court(self, surface):
        dash_len = 16
        gap_len = 12
        cx = self.width // 2
        for y in range(20, self.height - 20, dash_len + gap_len):
            pygame.draw.line(surface, (0, 180, 255), (cx, y), (cx, y + dash_len), 3)

        pygame.draw.circle(surface, (0, 180, 255), (cx, self.height // 2), 60, width=2)
        pygame.draw.circle(surface, (0, 245, 255), (cx, self.height // 2), 6, width=0)

    def draw_hud(self, surface, score1, score2, p1_name, p2_name, rally_count, ball_speed, powerups_enabled, muted):
        self.draw_center_court(surface)

        s1_surf = self.score_font.render(str(score1), True, (0, 245, 255))
        s2_surf = self.score_font.render(str(score2), True, (255, 0, 128))
        
        surface.blit(s1_surf, (self.width // 4 - s1_surf.get_width() // 2, 25))
        surface.blit(s2_surf, (3 * self.width // 4 - s2_surf.get_width() // 2, 25))

        p1_lbl = self.sub_font.render(p1_name, True, (0, 200, 255))
        p2_lbl = self.sub_font.render(p2_name, True, (255, 60, 150))
        surface.blit(p1_lbl, (self.width // 4 - p1_lbl.get_width() // 2, 5))
        surface.blit(p2_lbl, (3 * self.width // 4 - p2_lbl.get_width() // 2, 5))

        stat_text = f"RALLY: {rally_count}   |   BALL SPEED: {int(ball_speed * 10)} KM/H   |   MUTE: {'YES' if muted else 'NO (M)'}"
        stat_surf = self.hud_font.render(stat_text, True, (150, 180, 210))
        surface.blit(stat_surf, (self.width // 2 - stat_surf.get_width() // 2, self.height - 25))

    def draw_ready_overlay(self, surface, p1_ready, p2_ready, p1_is_local):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((5, 10, 20, 180))
        surface.blit(overlay, (0, 0))

        cx = self.width // 2
        cy = self.height // 2 - 40

        title_surf = self.title_font.render("WAITING FOR BOTH PLAYERS", True, (255, 215, 0))
        surface.blit(title_surf, title_surf.get_rect(center=(cx, cy - 60)))

        # Badges
        b1_col = (0, 230, 120) if p1_ready else (140, 150, 170)
        b2_col = (0, 230, 120) if p2_ready else (140, 150, 170)
        
        b1_txt = "PLAYER 1: READY ✅" if p1_ready else "PLAYER 1: NOT READY ⏳"
        b2_txt = "PLAYER 2: READY ✅" if p2_ready else "PLAYER 2: NOT READY ⏳"

        p1_surf = self.sub_font.render(b1_txt, True, b1_col)
        p2_surf = self.sub_font.render(b2_txt, True, b2_col)

        surface.blit(p1_surf, (cx - 220, cy))
        surface.blit(p2_surf, (cx + 30, cy))

        local_ready = p1_ready if p1_is_local else p2_ready
        hint_text = "Press [SPACE] or click READY button below!" if not local_ready else "Waiting for other player to press READY..."
        hint_surf = self.btn_font.render(hint_text, True, (0, 245, 255))
        surface.blit(hint_surf, hint_surf.get_rect(center=(cx, cy + 50)))

    def draw_pause_overlay(self, surface):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((5, 10, 20, 200))
        surface.blit(overlay, (0, 0))

        title_surf = self.title_font.render("GAME PAUSED", True, (0, 245, 255))
        t_rect = title_surf.get_rect(center=(self.width // 2, self.height // 3))
        surface.blit(title_surf, t_rect)

        sub_surf = self.sub_font.render("Press ESC or P to Resume", True, (200, 220, 240))
        s_rect = sub_surf.get_rect(center=(self.width // 2, self.height // 3 + 60))
        surface.blit(sub_surf, s_rect)

    def draw_game_over(self, surface, winner_text):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((5, 10, 20, 220))
        surface.blit(overlay, (0, 0))

        title_surf = self.title_font.render("VICTORY!", True, (255, 215, 0))
        t_rect = title_surf.get_rect(center=(self.width // 2, self.height // 3 - 20))
        surface.blit(title_surf, t_rect)

        w_surf = self.sub_font.render(winner_text, True, (0, 245, 255))
        w_rect = w_surf.get_rect(center=(self.width // 2, self.height // 3 + 50))
        surface.blit(w_surf, w_rect)
