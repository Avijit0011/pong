import sys
import pygame
from game import PongGame
from network import trigger_firewall_prompt

def main():
    # Pre-trigger Windows Defender Firewall access prompt on OS startup
    trigger_firewall_prompt()

    # Initialize Pygame core modules
    pygame.init()
    pygame.font.init()
    
    # Configure desktop window
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 600
    
    pygame.display.set_caption("Neon Pong 2D")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    
    # Instantiate game engine
    game = PongGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    running = True
    while running:
        # Event pump & dispatcher
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game.handle_event(event)
                
        # Game step logic update
        game.update()
        
        # Frame rendering
        game.draw(screen)
        pygame.display.flip()
        
        # Cap frame rate at smooth 60 FPS
        clock.tick(60)

    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
