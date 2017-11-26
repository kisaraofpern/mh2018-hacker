import pygame
import time

pygame.init()
pygame.font.init()

myfont = pygame.font.SysFont("Comic Sans MS", 300)
screen = pygame.display.set_mode((0,0))
white = (255, 255, 255)

class text_box():
    # A textbox is comprised of its Surface (what is being rendered)
    # and its Rect (where it is rendered).
    def __init__(left, top, width, height):
        self.left = left
        self.top = top
        self.width = width
        self.height = height

        # Initialize the Surface for the textbox.
        # This is what the text will render onto.
        self.text = pygame.Surface([self.width, self.height])
        self.text.fill(white)

        # Get the Rect for the textbox.
        # Update the position based on initialization values.
        self.box = self.text.get_rect()
        self.box.move(self.left, self.top)

        # Initialize the Font object for the textbox.
        self.font = pygame.font.SysFont("Comic Sans MS", 300)

    def add_text(string):
        # pygame.font.Font.render draws text on a new Surface and returns
        # that surface.
        # add_text will apply that surface to the textbox.
        # Because it is dependent on `render`, `add_text` is NOT thread-safe:
        # Only a single thread can render text at a time.
        # TODO: collision handling, maybe.
        this_text = self.font.render(string, False, (255, 0, 0))
        self.text.blit(this_text, self.box)

    def render():
        screen.blit()
        pygame.display.update(self.box)


while True:
    my_text_box = text_box(500, 500, 200, 100)
    screen.blit(my_text_box)
    for x in range(0, 10):
        # screen.fill((255, 255, 255))
        my_text_box.add_text(chr(x+48))
        my_text_box.render();
        # screen.blit(myfont.render(chr(x+48), False, (255,0,0)),(0,0))
        # pygame.display.flip()
        time.sleep(1)
    pygame.quit()
