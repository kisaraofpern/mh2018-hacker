import pygame
import time

pygame.init()
pygame.font.init()

myfont = pygame.font.SysFont("Comic Sans MS", 300)
screen = pygame.display.set_mode((0,0))

while True:
    for x in range(0, 10):
        screen.fill((255,255,255))
        screen.blit(myfont.render(chr(x+48), False, (255,0,0)),(0,0))
        pygame.display.flip()
        time.sleep(1)
