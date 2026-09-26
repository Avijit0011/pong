import pygame
import time

class Button:
    def __init__(self, x, y, width, height, text, font, color=(30, 41, 59), hover_color=(51, 65, 85), text_color=(241, 245, 249)):
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
        border_col = (56, 189, 248) if self.is_hovered else (71, 85, 105)
        
        # Subtle ambient border shadow if hovered
        if self.is_hovered:
            glow_surf = pygame.Surface((self.rect.width + 8, self.rect.height + 8), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (56, 189, 248, 30), (0, 0, self.rect.width + 8, self.rect.height + 8), border_radius=8)
            surface.blit(glow_surf, (self.rect.x - 4, self.rect.y - 4))

        # Main button body
        pygame.draw.rect(surface, bg_col, self.rect, border_radius=6)
        pygame.draw.rect(surface, border_col, self.rect, width=1, border_radius=6)
        
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
        bg_col = (15, 23, 42) if not self.active else (30, 41, 59)
        border_col = (56, 189, 248) if self.active else (71, 85, 105)
        
        pygame.draw.rect(surface, bg_col, self.rect, border_radius=6)
        pygame.draw.rect(surface, border_col, self.rect, width=1, border_radius=6)
        
        display_text = self.text + ("|" if self.active and (pygame.time.get_ticks() // 500) % 2 == 0 else "")
        txt_surf = self.font.render(display_text, True, (241, 245, 249))
        surface.blit(txt_surf, (self.rect.x + 15, self.rect.y + (self.rect.height - txt_surf.get_height()) // 2))


class ChatSystem:
    def __init__(self, font):
        self.font = font
        self.messages = []  # list of {"sender": "P1", "text": "...", "time": timestamp, "color": tuple}
        self.active = False
        self.input_text = ""

    def add_message(self, sender, text, color=(56, 189, 248)):
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
        now = time.time()
        start_y = screen_height - 160
        
        chat_box = pygame.Surface((340, 105), pygame.SRCALPHA)
        chat_box.fill((15, 23, 42, 180))
        pygame.draw.rect(chat_box, (51, 65, 85, 120), (0, 0, 340, 105), width=1, border_radius=6)
        surface.blit(chat_box, (15, start_y))

        recent_msgs = [m for m in self.messages if now - m["time"] < 12.0 or self.active][-5:]
        line_y = start_y + 8
        for msg in recent_msgs:
            prefix_color = msg["color"]
            sender_surf = self.font.render(f"[{msg['sender']}]: ", True, prefix_color)
            txt_surf = self.font.render(msg["text"], True, (226, 232, 240))
            
            surface.blit(sender_surf, (22, line_y))
            surface.blit(txt_surf, (22 + sender_surf.get_width(), line_y))
            line_y += 19

        if self.active:
            inp_box_surf = pygame.Surface((340, 30), pygame.SRCALPHA)
            inp_box_surf.fill((30, 41, 59, 230))
            pygame.draw.rect(inp_box_surf, (56, 189, 248), (0, 0, 340, 30), width=1, border_radius=6)
            surface.blit(inp_box_surf, (15, screen_height - 48))

            prompt = f"CHAT: {self.input_text}" + ("|" if (pygame.time.get_ticks() // 400) % 2 == 0 else "")
            p_surf = self.font.render(prompt, True, (56, 189, 248))
            surface.blit(p_surf, (25, screen_height - 42))
        else:
            hint_surf = self.font.render("Press [T] or [ENTER] to Chat", True, (100, 116, 139))
            surface.blit(hint_surf, (22, screen_height - 48))


class UIRenderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        pygame.font.init()
        self.title_font = pygame.font.SysFont("Segoe UI", 48, bold=True) or pygame.font.SysFont("Helvetica Neue", 48, bold=True) or pygame.font.Font(None, 52)
        self.sub_font = pygame.font.SysFont("Segoe UI", 20, bold=True) or pygame.font.SysFont("Helvetica Neue", 20, bold=True) or pygame.font.Font(None, 22)
        self.score_font = pygame.font.SysFont("Segoe UI", 56, bold=True) or pygame.font.SysFont("Helvetica Neue", 56, bold=True) or pygame.font.Font(None, 60)
        self.hud_font = pygame.font.SysFont("Segoe UI", 14) or pygame.font.SysFont("Arial", 14) or pygame.font.Font(None, 16)
        self.btn_font = pygame.font.SysFont("Segoe UI", 16, bold=True) or pygame.font.SysFont("Arial", 16, bold=True) or pygame.font.Font(None, 18)

        # Pre-render subtle radial vignette background surface for extra depth
        self.bg_surf = pygame.Surface((width, height))
        self.bg_surf.fill((11, 15, 25))
        cx, cy = width // 2, height // 2
        max_r = int((cx**2 + cy**2)**0.5)
        
        # Radial gradient overlay steps
        vignette = pygame.Surface((width, height), pygame.SRCALPHA)
        for r in range(max_r, 0, -35):
            alpha = int(45 * (r / max_r)**1.5)
            pygame.draw.circle(vignette, (5, 8, 15, alpha), (cx, cy), r)
        self.bg_surf.blit(vignette, (0, 0))

        self.score1_pop = 0.0
        self.score2_pop = 0.0

    def trigger_score_pop(self, scorer):
        if scorer == 1:
            self.score1_pop = 1.0
        else:
            self.score2_pop = 1.0

    def draw_background(self, surface):
        surface.blit(self.bg_surf, (0, 0))
        
        # Draw sleek minimalist arena border line
        border_rect = pygame.Rect(15, 15, self.width - 30, self.height - 30)
        pygame.draw.rect(surface, (30, 41, 59), border_rect, width=1, border_radius=8)
        
        # Accent corner brackets
        c_len = 16
        c_col = (51, 65, 85)
        # Top-Left
        pygame.draw.line(surface, c_col, (15, 15), (15 + c_len, 15), 2)
        pygame.draw.line(surface, c_col, (15, 15), (15, 15 + c_len), 2)
        # Top-Right
        pygame.draw.line(surface, c_col, (self.width - 15, 15), (self.width - 15 - c_len, 15), 2)
        pygame.draw.line(surface, c_col, (self.width - 15, 15), (self.width - 15, 15 + c_len), 2)
        # Bottom-Left
        pygame.draw.line(surface, c_col, (15, self.height - 15), (15 + c_len, self.height - 15), 2)
        pygame.draw.line(surface, c_col, (15, self.height - 15), (15, self.height - 15 - c_len), 2)
        # Bottom-Right
        pygame.draw.line(surface, c_col, (self.width - 15, self.height - 15), (self.width - 15 - c_len, self.height - 15), 2)
        pygame.draw.line(surface, c_col, (self.width - 15, self.height - 15), (self.width - 15, self.height - 15 - c_len), 2)

    def draw_center_court(self, surface):
        dash_len = 12
        gap_len = 10
        cx = self.width // 2
        line_color = (30, 41, 59)
        for y in range(25, self.height - 25, dash_len + gap_len):
            pygame.draw.line(surface, line_color, (cx, y), (cx, y + dash_len), 2)

        pygame.draw.circle(surface, line_color, (cx, self.height // 2), 55, width=1)
        pygame.draw.circle(surface, (51, 65, 85), (cx, self.height // 2), 4, width=0)

    def draw_hud(self, surface, score1, score2, p1_name, p2_name, rally_count, ball_speed, powerups_enabled, muted):
        self.draw_center_court(surface)

        self.score1_pop *= 0.88
        self.score2_pop *= 0.88

        s1_surf = self.score_font.render(str(score1), True, (56, 189, 248))
        s2_surf = self.score_font.render(str(score2), True, (244, 63, 94))
        
        if self.score1_pop > 0.05:
            scale = 1.0 + 0.3 * self.score1_pop
            nw, nh = int(s1_surf.get_width() * scale), int(s1_surf.get_height() * scale)
            s1_surf = pygame.transform.smoothscale(s1_surf, (max(1, nw), max(1, nh)))
            
        if self.score2_pop > 0.05:
            scale = 1.0 + 0.3 * self.score2_pop
            nw, nh = int(s2_surf.get_width() * scale), int(s2_surf.get_height() * scale)
            s2_surf = pygame.transform.smoothscale(s2_surf, (max(1, nw), max(1, nh)))

        surface.blit(s1_surf, (self.width // 4 - s1_surf.get_width() // 2, 28 - (s1_surf.get_height() - 56) // 2))
        surface.blit(s2_surf, (3 * self.width // 4 - s2_surf.get_width() // 2, 28 - (s2_surf.get_height() - 56) // 2))

        p1_lbl = self.sub_font.render(p1_name.upper(), True, (148, 163, 184))
        p2_lbl = self.sub_font.render(p2_name.upper(), True, (148, 163, 184))
        surface.blit(p1_lbl, (self.width // 4 - p1_lbl.get_width() // 2, 8))
        surface.blit(p2_lbl, (3 * self.width // 4 - p2_lbl.get_width() // 2, 8))

        stat_text = f"RALLY: {rally_count}   |   AUDIO: {'MUTED (M)' if muted else 'ACTIVE (M)'}"
        stat_surf = self.hud_font.render(stat_text, True, (100, 116, 139))
        surface.blit(stat_surf, (self.width // 2 - stat_surf.get_width() // 2, self.height - 24))

    def draw_ready_overlay(self, surface, p1_ready, p2_ready, p1_is_local):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((11, 15, 25, 200))
        surface.blit(overlay, (0, 0))

        cx = self.width // 2
        cy = self.height // 2 - 40

        title_surf = self.title_font.render("WAITING FOR PLAYERS", True, (241, 245, 249))
        surface.blit(title_surf, title_surf.get_rect(center=(cx, cy - 60)))

        b1_col = (52, 211, 153) if p1_ready else (148, 163, 184)
        b2_col = (52, 211, 153) if p2_ready else (148, 163, 184)
        
        b1_txt = "PLAYER 1: READY" if p1_ready else "PLAYER 1: NOT READY"
        b2_txt = "PLAYER 2: READY" if p2_ready else "PLAYER 2: NOT READY"

        p1_surf = self.sub_font.render(b1_txt, True, b1_col)
        p2_surf = self.sub_font.render(b2_txt, True, b2_col)

        surface.blit(p1_surf, (cx - 220, cy))
        surface.blit(p2_surf, (cx + 30, cy))

        local_ready = p1_ready if p1_is_local else p2_ready
        hint_text = "Press SPACE or click READY to begin" if not local_ready else "Waiting for opponent to click READY..."
        hint_surf = self.btn_font.render(hint_text, True, (56, 189, 248))
        surface.blit(hint_surf, hint_surf.get_rect(center=(cx, cy + 50)))

    def draw_pause_overlay(self, surface):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((11, 15, 25, 210))
        surface.blit(overlay, (0, 0))

        title_surf = self.title_font.render("GAME PAUSED", True, (241, 245, 249))
        t_rect = title_surf.get_rect(center=(self.width // 2, self.height // 3))
        surface.blit(title_surf, t_rect)

        sub_surf = self.sub_font.render("Press ESC or P to Resume", True, (148, 163, 184))
        s_rect = sub_surf.get_rect(center=(self.width // 2, self.height // 3 + 55))
        surface.blit(sub_surf, s_rect)

    def draw_game_over(self, surface, winner_text, stats=None):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((11, 15, 25, 220))
        surface.blit(overlay, (0, 0))

        cx = self.width // 2

        title_surf = self.title_font.render("MATCH COMPLETE", True, (241, 245, 249))
        t_rect = title_surf.get_rect(center=(cx, 110))
        surface.blit(title_surf, t_rect)

        w_surf = self.sub_font.render(winner_text.upper(), True, (56, 189, 248))
        w_rect = w_surf.get_rect(center=(cx, 160))
        surface.blit(w_surf, w_rect)

        if stats:
            card_w, card_h = 360, 105
            card_x, card_y = cx - card_w // 2, 195
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            card_surf.fill((30, 41, 59, 180))
            pygame.draw.rect(card_surf, (56, 189, 248), (0, 0, card_w, card_h), width=1, border_radius=8)
            surface.blit(card_surf, (card_x, card_y))

            s1 = self.btn_font.render(f"FINAL SCORE:  P1 [{stats.get('p1_score', 0)}] - [{stats.get('p2_score', 0)}] P2", True, (241, 245, 249))
            s2 = self.hud_font.render(f"LONGEST RALLY RECORD:  {stats.get('max_rally', 0)} HITS", True, (148, 163, 184))
            s3 = self.hud_font.render(f"PEAK BALL VELOCITY:  {stats.get('max_speed', 0.0):.1f} PX/F", True, (148, 163, 184))

            surface.blit(s1, s1.get_rect(center=(cx, card_y + 28)))
            surface.blit(s2, s2.get_rect(center=(cx, card_y + 58)))
            surface.blit(s3, s3.get_rect(center=(cx, card_y + 82)))
