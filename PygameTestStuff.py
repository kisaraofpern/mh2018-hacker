"""Pygame testbed"""
import pygame
from pygame.locals import *

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
SCREENWIDTH = 640
SCREENHEIGHT = 360

class TextBox(object):
    """ A textbox is comprised of its Surface (what is being rendered) and its Rect (where it is rendered). """
    def __init__(self, left, top, width, height):
        self.left = left
        self.top = top
        self.width = width
        self.height = height

        # Initialize the Surface for the textbox.
        # This is what the text will render onto.
        self.text = pygame.Surface([self.width, self.height])
        self.text.fill(YELLOW)

        # Get the Rect for the textbox.
        # Update the position based on initialization values.
        self.box = self.text.get_rect()
        self.box.move(self.left, self.top)

        # Initialize the Font object for the textbox.
        self.font = pygame.font.SysFont("Comic Sans MS", 300)

    def add_text(self, string):
        """Draws text onto a new Surface and returns that Surface"""
        # pygame.font.Font.render draws text on a new Surface and returns
        # that surface.
        # add_text will apply that surface to the textbox.
        # Because it is dependent on `render`, `add_text` is NOT thread-safe:
        # Only a single thread can render text at a time.
        # TODO: collision handling, maybe.
        this_text = self.font.render(string, True, BLACK)
        this_box = this_text.get_rect()
        this_box.move(self.left, self.top)
        self.text.blit(this_text, this_box)

    # def render(self):
    #     """Renders the textbox"""
    #     SCREEN.blit(self.text, self.box)
    #     pygame.display.update(self.box)

global SCREEN
pygame.init()
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption("Cannonball Run")

pygame.font.init()
MYFONT = pygame.font.SysFont("Comic Sans MS", 300)

while True:
    pygame.event.pump()
    # pygame.font.init()
    # my_text_box = TextBox(500, 500, 200, 100)
    # SCREEN.blit(my_text_box.text, my_text_box.box)
    for x in range(0, 10):
        SCREEN.fill(RED)
        # my_text_box.add_text(chr(x+48))
        print "About to render..."
        # my_text_box.render()
        font_object = MYFONT.render(chr(x+48), False, BLACK)
        SCREEN.blit(font_object, (0, 0))
        pygame.display.update()
        print x
        pygame.time.delay(2000)
