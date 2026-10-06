import math
import random
import pygame

class Ball:
    """
    Represents the ball object in the game. Handles physics, bouncing, 
    squash and stretch animation, 3D sphere rendering, and trail rendering.
    """
    def __init__(self, x, y, radius=10, color=(241, 245, 249), glow_color=(56, 189, 248)):
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
        
        self.squash_x = 1.0
        self.squash_y = 1.0
        
        self.trail = []  # List of previous positions (x, y)
        self.max_trail_len = 8
        self.rally_count = 0
        self.rotation = 0.0
        
        self.reset(direction=random.choice([-1, 1]))

    def reset(self, direction=1):
        self.x = self.start_x
        self.y = self.start_y
        self.speed = self.base_speed
        
        # Launch angle between -35 deg and +35 deg
        angle = math.radians(random.uniform(-35, 35))
        self.vx = direction * self.speed * math.cos(angle)
        self.vy = self.speed * math.sin(angle)
        self.squash_x = 1.0
        self.squash_y = 1.0
        self.trail.clear()
        self.rally_count = 0
        self.rotation = 0.0

    def update(self, arena_width, arena_height, sound_engine=None, particle_system=None):
        # Lerp squash back to normal
        self.squash_x += (1.0 - self.squash_x) * 0.2
        self.squash_y += (1.0 - self.squash_y) * 0.2

        # 3D Rotation based on speed
        self.rotation += math.hypot(self.vx, self.vy) * 0.08

        # Store current position in trail
        self.trail.insert(0, (self.x, self.y))
        if len(self.trail) > self.max_trail_len:
            self.trail.pop()

        # Update coordinates
        self.x += self.vx
        self.y += self.vy

        # Emit speed trail particles if ball moving fast
        if particle_system and self.speed > 11.0:
            particle_system.spawn_speed_trail(self.x, self.y, color=self.glow_color, count=1)

        # Wall collisions (Top and Bottom boundaries)
        top_bound = 15 + self.radius
        bottom_bound = arena_height - 15 - self.radius

        if self.y <= top_bound:
            self.y = top_bound
            self.vy = abs(self.vy)
            self.squash_x = 1.35
            self.squash_y = 0.65
            if sound_engine:
                sound_engine.play('wall_hit')
            if particle_system:
                particle_system.spawn_impact_sparks(self.x, self.y, 0, color=(241, 245, 249), count=6)

        elif self.y >= bottom_bound:
            self.y = bottom_bound
            self.vy = -abs(self.vy)
            self.squash_x = 1.35
            self.squash_y = 0.65
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
            paddle.hit_flash = 1.0
            
            self.squash_x = 0.65
            self.squash_y = 1.35
            
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
                if self.rally_count > 0 and self.rally_count % 5 == 0:
                    sound_engine.play('rally_milestone')
                else:
                    sound_engine.play('paddle_hit')
            if particle_system:
                sparks_color = paddle.color
                particle_system.spawn_impact_sparks(self.x, self.y, direction, color=sparks_color, count=8)
            
            return True
        return False

    def _render_3d_sphere_surface(self, radius, rotation=0.0):
        """
        Renders a volumetric 3D shaded sphere texture with specular highlights,
        ambient occlusion, and rotating 3D surface seams.
        """
        padding = 10
        size = int((radius + padding) * 2)
        cx, cy = size / 2.0, size / 2.0
        
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # 1. Outer Glow Aura (Soft emissive 3D halo)
        glow_r = radius * 1.45
        for g_step in range(8, 0, -1):
            r_g = radius + (glow_r - radius) * (g_step / 8.0)
            alpha_g = int(35 * (1.0 - g_step / 8.0))
            glow_col = (*self.glow_color[:3], alpha_g)
            pygame.draw.circle(surf, glow_col, (int(cx), int(cy)), int(r_g))

        # 2. 3D Spherical Radial Shading (Diffuse & Ambient Occlusion)
        # Light source from top-left offset (-0.35, -0.35)
        lx = cx - radius * 0.35
        ly = cy - radius * 0.35
        
        # Shadow base color (bottom-right edge)
        shadow_col = (
            max(20, int(self.color[0] * 0.25)),
            max(25, int(self.color[1] * 0.30)),
            max(45, int(self.color[2] * 0.45))
        )
        
        # Concentric gradient steps from outer radius down to inner light center
        num_steps = max(12, int(radius * 2))
        for step in range(num_steps, 0, -1):
            t = step / float(num_steps)  # 1.0 at outer edge, ~0 at light center
            
            # Interpolate circle center towards light source
            cur_cx = cx + (lx - cx) * (1.0 - t)
            cur_cy = cy + (ly - cy) * (1.0 - t)
            cur_r = radius * t
            
            # Smooth non-linear color interpolation for 3D sphere curvature
            curve_t = math.pow(1.0 - t, 0.75)  # spherical curve falloff
            r_c = int(shadow_col[0] + (self.color[0] - shadow_col[0]) * curve_t)
            g_c = int(shadow_col[1] + (self.color[1] - shadow_col[1]) * curve_t)
            b_c = int(shadow_col[2] + (self.color[2] - shadow_col[2]) * curve_t)
            
            # Enhance light intensity near highlight center
            if curve_t > 0.6:
                boost = (curve_t - 0.6) / 0.4
                r_c = min(255, int(r_c + (255 - r_c) * boost * 0.7))
                g_c = min(255, int(g_c + (255 - g_c) * boost * 0.7))
                b_c = min(255, int(b_c + (255 - b_c) * boost * 0.7))
                
            pygame.draw.circle(surf, (r_c, g_c, b_c, 255), (int(cur_cx), int(cur_cy)), max(1, int(cur_r)))

        # 3. 3D Rotating Seam / Meridian Arc (Rolling 3D visual feedback)
        seam_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        sin_rot = math.sin(rotation)
        cos_rot = math.cos(rotation)
        
        # Projection of 3D curved meridian line on sphere surface
        arc_w = int(radius * 1.5 * abs(cos_rot))
        arc_h = int(radius * 0.9)
        arc_x = int(cx - arc_w / 2.0)
        arc_y = int(cy - arc_h / 2.0 + radius * 0.3 * sin_rot)
        
        if arc_w > 2 and arc_h > 2:
            arc_rect = pygame.Rect(arc_x, arc_y, arc_w, arc_h)
            seam_color = (
                min(255, int(self.glow_color[0] * 0.8)),
                min(255, int(self.glow_color[1] * 0.8)),
                min(255, int(self.glow_color[2] * 0.8)),
                int(120 * abs(cos_rot))
            )
            pygame.draw.arc(seam_surf, seam_color, arc_rect, math.pi * 0.1, math.pi * 0.9, width=2)
            
            # Mask seam within sphere boundary
            sphere_mask = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(sphere_mask, (255, 255, 255, 255), (int(cx), int(cy)), int(radius))
            seam_surf.blit(sphere_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            surf.blit(seam_surf, (0, 0))

        # 4. Secondary Ambient Rim Light (Bottom-Right edge reflection)
        rim_x = cx + radius * 0.45
        rim_y = cy + radius * 0.45
        rim_r = max(2, int(radius * 0.4))
        rim_col = (
            min(255, int(self.glow_color[0] + 50)),
            min(255, int(self.glow_color[1] + 50)),
            min(255, int(self.glow_color[2] + 50)),
            90
        )
        rim_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(rim_surf, rim_col, (int(rim_x), int(rim_y)), rim_r)
        # Mask rim within sphere
        pygame.draw.circle(rim_surf, (0, 0, 0, 0), (int(cx), int(cy)), int(radius), width=0)
        surf.blit(rim_surf, (0, 0))

        # 5. Primary Specular Highlight (Glossy top-left 3D shine)
        spec_x = int(cx - radius * 0.32)
        spec_y = int(cy - radius * 0.32)
        spec_r1 = max(2, int(radius * 0.35))
        spec_r2 = max(1, int(radius * 0.18))
        
        # Soft glossy glow spot
        pygame.draw.circle(surf, (255, 255, 255, 180), (spec_x, spec_y), spec_r1)
        # Intense core highlight
        pygame.draw.circle(surf, (255, 255, 255, 240), (spec_x - 1, spec_y - 1), spec_r2)

        return surf

    def draw(self, surface):
        # 1. Draw 3D Motion Trail (Fading 3D sphere ghosts)
        for i, (tx, ty) in enumerate(reversed(self.trail)):
            alpha_ratio = (i + 1) / (len(self.trail) + 1)
            trail_alpha = int(140 * alpha_ratio)
            trail_scale = 0.5 + 0.5 * alpha_ratio
            
            t_radius = self.radius * trail_scale
            t_surf = self._render_3d_sphere_surface(t_radius, self.rotation)
            
            # Apply alpha transparency to trail ghost
            t_surf_ghost = t_surf.copy()
            t_surf_ghost.fill((255, 255, 255, trail_alpha), special_flags=pygame.BLEND_RGBA_MULT)
            
            t_rect = t_surf_ghost.get_rect(center=(int(tx), int(ty)))
            surface.blit(t_surf_ghost, t_rect)

        # 2. Draw 3D Ground Drop Shadow (Depth perspective onto court)
        shadow_w = int(self.radius * 2.2 * self.squash_x)
        shadow_h = max(3, int(self.radius * 0.9 * self.squash_y))
        shadow_surf = pygame.Surface((shadow_w + 4, shadow_h + 4), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 75), (2, 2, shadow_w, shadow_h))
        
        # Position shadow offset down and right from ball center
        shadow_rect = shadow_surf.get_rect(center=(int(self.x + 4), int(self.y + self.radius * 0.6 + 4)))
        surface.blit(shadow_surf, shadow_rect)

        # 3. Render and Blit Main 3D Ball with Squash & Stretch
        base_3d_surf = self._render_3d_sphere_surface(self.radius, self.rotation)
        
        target_w = int(base_3d_surf.get_width() * self.squash_x)
        target_h = int(base_3d_surf.get_height() * self.squash_y)
        
        if target_w > 0 and target_h > 0:
            if self.squash_x != 1.0 or self.squash_y != 1.0:
                final_surf = pygame.transform.smoothscale(base_3d_surf, (target_w, target_h))
            else:
                final_surf = base_3d_surf
                
            rect = final_surf.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(final_surf, rect)


