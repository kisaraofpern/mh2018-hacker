"""Pygame testbed"""
import pygame
from pygame.locals import *

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
SCREENWIDTH = 1280
SCREENHEIGHT = 720

class TextBox(object):
    """ A textbox is comprised of its Surface (what is being rendered) and its Rect (where it is rendered). """
    def __init__(self, left, top, width, height, fill_color=BLACK):
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.fill_color = fill_color

        # Initialize the Surface for the textbox.
        # This is what the text will render onto.
        self.text = pygame.Surface([self.width, self.height])
        self.text.fill(self.fill_color)

        # Get the Rect for the textbox.
        # Update the position based on initialization values.
        self.box = self.text.get_rect()
        self.box = self.box.move(self.left, self.top)

    def draw_text(self, string, text_color=WHITE, font="Droid Sans Fallback Full", font_size=40):
        """Draws text onto a new Surface and returns that Surface"""
        # pygame.font.Font.render draws text on a new Surface and returns
        # that surface.
        # add_text will apply that surface to the textbox.
        # Because it is dependent on `render`, `add_text` is NOT thread-safe:
        # Only a single thread can render text at a time.
        self.font = pygame.font.SysFont(font, font_size)
        this_text = self.font.render(string, True, text_color)
        SCREEN.fill(BLACK)
        SCREEN.blit(self.text, (self.left, self.top))
        self.text.fill(self.fill_color)
        self.text.blit(this_text, (25,15))
        pygame.display.update()

    def render(self):
        """Renders the textbox"""
        SCREEN.blit(self.text, (self.left, self.top))
        pygame.display.update(self.box)

global SCREEN
pygame.init()
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption("Cannonball Run")

pygame.font.init()
MYFONT = pygame.font.SysFont("Droid Sans Fallback Full", 20)

while True:
    pygame.event.pump()
    pygame.font.init()
    my_text_box = TextBox(500, 500, 200, 100)
    SCREEN.blit(my_text_box.text, my_text_box.box)
    for x in range(0, 10):
        # SCREEN.fill(RED)
        my_text_box.add_text(chr(x+48))
        # print "About to render..."
        # my_text_box.render()
        # font_object = MYFONT.render(chr(x+48), False, BLACK)
        # SCREEN.blit(font_object, (0, 0))
        # pygame.display.update()
        print x
        pygame.time.delay(500)
