import os
import math
import unittest

# Run headless without opening GUI windows
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
pygame.init()

from ball import Ball
from paddle import Paddle
from powerup import PowerUp, PowerUpManager, POWERUP_TYPES
from particles import ParticleSystem
from audio import SoundEngine
from game import PongGame

class TestBallPhysics(unittest.TestCase):
    def setUp(self):
        self.ball = Ball(500, 300)

    def test_ball_initialization(self):
        self.assertEqual(self.ball.x, 500)
        self.assertEqual(self.ball.y, 300)
        self.assertEqual(self.ball.rally_count, 0)
        self.assertGreater(self.ball.speed, 0)

    def test_wall_bounce_top(self):
        self.ball.y = 10
        self.ball.vy = -5.0
        self.ball.update(1000, 600)
        self.assertGreater(self.ball.vy, 0)  # Reversed downward

    def test_wall_bounce_bottom(self):
        self.ball.y = 590
        self.ball.vy = 5.0
        self.ball.update(1000, 600)
        self.assertLess(self.ball.vy, 0)  # Reversed upward

    def test_paddle_collision_reflection(self):
        paddle = Paddle(40, 300, is_ai=False)
        self.ball.x = 42
        self.ball.y = 300
        self.ball.vx = -8.0
        hit = self.ball.check_paddle_collision(paddle)
        self.assertTrue(hit)
        self.assertEqual(self.ball.rally_count, 1)
        self.assertGreater(self.ball.vx, 0)  # Bounced right


class TestPaddleLogic(unittest.TestCase):
    def setUp(self):
        self.paddle = Paddle(40, 300, is_ai=False)

    def test_paddle_bounds_top(self):
        self.paddle.y = 5
        self.paddle.update(600, up_pressed=True, down_pressed=False)
        self.assertGreaterEqual(self.paddle.y, 15 + self.paddle.height / 2.0)

    def test_paddle_bounds_bottom(self):
        self.paddle.y = 595
        self.paddle.update(600, up_pressed=False, down_pressed=True)
        self.assertLessEqual(self.paddle.y, 600 - 15 - self.paddle.height / 2.0)

    def test_powerup_application(self):
        # Extend
        base_h = self.paddle.height
        self.paddle.apply_powerup("EXTEND", duration=10)
        self.assertGreater(self.paddle.height, base_h)
        for _ in range(10):
            self.paddle.update(600, False, False)
        self.assertEqual(self.paddle.height, base_h)

        # Shield
        self.paddle.apply_powerup("SHIELD")
        self.assertTrue(self.paddle.has_shield)

    def test_ai_difficulties(self):
        for diff in ["Easy", "Medium", "Hard", "Impossible"]:
            ai_paddle = Paddle(960, 300, is_ai=True)
            ai_paddle.ai_difficulty = diff
            ball = Ball(500, 300)
            ball.vx = 8.0
            ai_paddle.update(600, False, False, balls=[ball])
            self.assertTrue(ai_paddle.is_ai)


class TestPowerUpSystem(unittest.TestCase):
    def test_powerup_types(self):
        self.assertIn("SLOW_MO", POWERUP_TYPES)
        self.assertIn("SPEED", POWERUP_TYPES)
        self.assertIn("SHIELD", POWERUP_TYPES)
        self.assertIn("EXTEND", POWERUP_TYPES)
        self.assertIn("MULTIBALL", POWERUP_TYPES)

    def test_slowmo_effect(self):
        mgr = PowerUpManager()
        sound = SoundEngine()
        particles = ParticleSystem()
        p = PowerUp(500, 300, "SLOW_MO")
        mgr.powerups.append(p)

        ball = Ball(500, 300)
        ball.speed = 10.0
        ball.vx = 8.0
        ball.vy = 6.0
        p1 = Paddle(40, 300)
        p2 = Paddle(960, 300)

        mgr.update(1000, 600, [ball], p1, p2, sound, particles, lambda x, y, vx, vy: None)
        self.assertLess(ball.speed, 10.0)


class TestGameEngine(unittest.TestCase):
    def setUp(self):
        self.game = PongGame(1000, 600)

    def test_initial_state(self):
        self.assertEqual(self.game.state, "MENU")
        self.assertEqual(self.game.paddle1.score, 0)
        self.assertEqual(self.game.paddle2.score, 0)

    def test_reset_match(self):
        self.game.paddle1.score = 4
        self.game.reset_match()
        self.assertEqual(self.game.state, "PLAYING")
        self.assertEqual(self.game.paddle1.score, 0)
        self.assertEqual(self.game.paddle2.score, 0)

    def test_sound_mute_toggle(self):
        muted = self.game.sound.toggle_mute()
        self.assertTrue(muted)
        muted_again = self.game.sound.toggle_mute()
        self.assertFalse(muted_again)

if __name__ == '__main__':
    unittest.main()
