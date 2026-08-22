import pygame

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
        # Deep space dark slate gradient background
        surface.fill((10, 14, 26))
        
        # Subtle horizontal laser grid lines
        grid_color = (20, 30, 50)
        for y in range(0, self.height, 40):
            pygame.draw.line(surface, grid_color, (0, y), (self.width, y), 1)

    def draw_center_court(self, surface):
        # Dashed glowing center line
        dash_len = 16
        gap_len = 12
        cx = self.width // 2
        for y in range(20, self.height - 20, dash_len + gap_len):
            pygame.draw.line(surface, (0, 180, 255), (cx, y), (cx, y + dash_len), 3)

        # Center court pulse circle
        pygame.draw.circle(surface, (0, 180, 255), (cx, self.height // 2), 60, width=2)
        pygame.draw.circle(surface, (0, 245, 255), (cx, self.height // 2), 6, width=0)

    def draw_hud(self, surface, score1, score2, p1_name, p2_name, rally_count, ball_speed, powerups_enabled, muted):
        # Center line
        self.draw_center_court(surface)

        # Top Scores display
        s1_surf = self.score_font.render(str(score1), True, (0, 245, 255))
        s2_surf = self.score_font.render(str(score2), True, (255, 0, 128))
        
        surface.blit(s1_surf, (self.width // 4 - s1_surf.get_width() // 2, 25))
        surface.blit(s2_surf, (3 * self.width // 4 - s2_surf.get_width() // 2, 25))

        # Player names above scores
        p1_lbl = self.sub_font.render(p1_name, True, (0, 200, 255))
        p2_lbl = self.sub_font.render(p2_name, True, (255, 60, 150))
        surface.blit(p1_lbl, (self.width // 4 - p1_lbl.get_width() // 2, 5))
        surface.blit(p2_lbl, (3 * self.width // 4 - p2_lbl.get_width() // 2, 5))

        # Bottom stats bar (Rally & Ball speed)
        stat_text = f"RALLY: {rally_count}   |   BALL SPEED: {int(ball_speed * 10)} KM/H   |   MUTE: {'YES' if muted else 'NO (M)'}"
        stat_surf = self.hud_font.render(stat_text, True, (150, 180, 210))
        surface.blit(stat_surf, (self.width // 2 - stat_surf.get_width() // 2, self.height - 25))

    def draw_pause_overlay(self, surface):
        # Dark dimming layer
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((5, 10, 20, 200))
        surface.blit(overlay, (0, 0))

        # Pause Title
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
