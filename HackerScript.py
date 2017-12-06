"""Hacker Island Interaction game code"""
import time
import os
import random as rand
import numpy
import RPi.GPIO as GPIO
import pygame
from pygame.locals import *

## Pygame initializations
# These are necessary for the rest of the definitions,
# which is why they're here, instead of below with the other initializations.
print "Initializing Pygame..."
pygame.init()
pygame.font.init()
pygame.display.set_caption("Cannonball Run")
CLOCK = pygame.time.Clock()

print "Initializing Pygame display..."
SCREEN = pygame.display.set_mode((0, 0))
# pygame.display.toggle_fullscreen()

## Pin assignments
LEFT_BUTTON_INPUT  = 16
LEFT_BUTTON_LED    = 15
RIGHT_BUTTON_INPUT = 13
RIGHT_BUTTON_LED   = 11
SPEEDOMETER        = 00

## Default values for class definitions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SCREENWIDTH = SCREEN.get_width()
SCREENHEIGHT = SCREEN.get_height()

# This Rect will be used in reference to updating SCREEN
# after it has been enblittened.
MAIN_RECT = pygame.Rect(0, 0, SCREENWIDTH, SCREENHEIGHT)
FPS = 2

# Class Definitions
class Location(object):
    """A Location is a node on the decision tree that comprises the game."""
    def __init__(self, image, distance=100):
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (SCREENWIDTH, SCREENHEIGHT)).convert()
        self.left_link = "0"
        self.right_link = "0"
        self.distance = distance
        self.name = image.split(".")[0]

        # This will be computed during initialization of the program,
        # after initialization of the map.
        self.distance_to_caltech = 0

class TextBox(object):
    """ A textbox is comprised of its Surface (what is being rendered) and its Rect (where it is rendered). """
    def __init__(self, left, top, width, height, fill_color=WHITE):
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.fill_color = fill_color

        # Initialize the Surface for the textbox.
        # This is what the text will render onto.
        self.text = pygame.Surface([self.width, self.height])
        self.text.fill(fill_color)

        # Get the Rect for the textbox.
        # Update the position based on initialization values.
        self.box = self.text.get_rect()
        self.box = self.box.move(self.left, self.top)

## Global variables referenced in functions
print "Setting baseline values for dynamic variables..."
current_location = "highway_a"
current_speed = 0  # In meters/second. Calculated from the RPM of the bike
dirty_rects = []
distance_until_turn = 0 # In meters. The amount of distance remaining in the current distance.
speedometer_clock = 0 # In seconds. Time of last speedometer_tick.
speedometer_tick = 0 # In seconds. Time between ticks.
speedometer_readings = [] # Accumulation of speedometer readings, so the average can be taken.

# Functions
# Callbacks for user actions
def left_button(input):
    """Callback function for pressing the left button"""
    print "Left button press detected"

    event = pygame.event.Event(USEREVENT, action="LEFT_TURN")
    pygame.event.post(event)

def right_button(input):
    """Callback function for pressing the right button"""
    print "Right button press detected"

    event = pygame.event.Event(USEREVENT, action="RIGHT_TURN")
    pygame.event.post(event)

def quit_button(input):
    """Callback function for pressing the quit button"""
    print "Quit button detected! \n Quitting..."
    pygame.quit()
    GPIO.cleanup()

def update_speedometer_tick(input):
    """Callback function for updating the speedometer tick and speedometer
    clock, if enough time has passed."""
    global speedometer_clock
    global speedometer_tick

    speedometer_cooldown = 3 # seconds

    print "speedometer tick detected!"
    current_time = time.clock()

    if current_time - speedometer_clock > speedometer_cooldown:
        speedometer_tick = current_time - speedometer_clock
        speedometer_clock = current_time

    print str(speedometer_tick) + " milliseconds since last tick..."

# Calculations
def get_current_speed():
    """Calculation for getting the current speed"""
    global speedometer_readings
    pedal_circumference = 2

    # speed = float(pedal_circumference)/float(speedometer_tick)
    #
    # if len(speedometer_readings) > 5:
    #     average_speed = numpy.average(speedometer_readings)
    #     if (average_speed * 0.75) < speed < (average_speed * 1.25):
    #         if len(speedometer_readings) = 10:
    #             speedometer_readings.pop(0)
    #         speedometer_readings.append(speed)
    #
    # return numpy.average(speedometer_readings)
    return rand.randrange(4, 8)

def get_incremental_distance():
    global current_speed
    """Calculation for getting incremental distance since the last frame."""
    return ((current_speed+get_current_speed())/2)*(1/float(FPS))

def get_distance_to_caltech(location):
    """Calculation for getting the distance to CalTech, from a given location."""
    if location.name == "CalTech" or location.name.find("lost") > -1:
        return 0

    if location.name == "highway_j_full":
        return location.distance
    else:
        child_location = location_dict[location.left_link]
        if location.left_link.find("lost") > -1:
            child_location = location_dict[location.right_link]
        return location.distance + get_distance_to_caltech(child_location)

def get_current_distance_from_caltech(location):
    """Calculation for getting the ditance to CalTech.
    Used during the main game loop.
    Returns a string."""
    if location.name.find("lost") > -1:
        return "???"

    return str(location.distance_to_caltech - location.distance + distance_until_turn)

# Transformations
def change_location(location):
    """Updates the current location and blits the screen."""
    global current_location
    global dirty_rects
    global SCREEN
    current_location = location_dict[location]
    SCREEN.fill(BLACK)
    SCREEN.blit(current_location.image, (0, 0))
    dirty_rects.append(MAIN_RECT)

def draw_text(textbox, string, text_color=BLACK, font="Piboto", font_size=40):
    """Draws text onto a new Surface and returns that Surface"""
    global dirty_rects
    global SCREEN
    # pygame.font.Font.render draws text on a new Surface and returns
    # that surface.
    # draw_text will apply that surface to the textbox.
    # Because it is dependent on `render`, `add_text` is NOT thread-safe:
    # Only a single thread can render text at a time.
    margin_left = 25
    # margin_top to be calculated below

    textbox.font = pygame.font.SysFont(font, font_size, bold=True)
    this_text = textbox.font.render(string, True, text_color)

    margin_top = (textbox.text.get_height() - this_text.get_height())/2

    textbox.text.fill(textbox.fill_color)
    textbox.text.blit(this_text, (margin_left, margin_top))
    SCREEN.blit(textbox.text, (textbox.left, textbox.top))
    dirty_rects.append(textbox.box)

def update_display():
    """Updates all of the dirty rectangles in the display."""
    global dirty_rects
    pygame.display.update(dirty_rects)
    dirty_rects = []

def flash_text(textbox, string, delay=500, text_color=BLACK, font="Piboto", font_size=40, LED=""):
    """Flashes the text in the display three times"""
    for x in range(0, 3):
        draw_text(textbox, '', text_color, font, font_size)
        update_display()
        if LED:
            GPIO.output(LED, False)
        pygame.time.wait(delay)
        draw_text(textbox, string, text_color, font, font_size)
        update_display()
        if LED:
            GPIO.output(LED, True)
        pygame.time.wait(delay)

def draw_all_stats():
    global current_speed, distance_until_turn, speed_textbox, distance_until_turn_textbox, destination_distance_textbox
    """Draws Speed, Distance Until Turn, and Distance to CalTech."""
    draw_text(speed_textbox, "Speed: " + str(current_speed) + " m/s")
    draw_text(distance_until_turn_textbox, "Distance Until Turn: " + str(distance_until_turn) + "m")
    draw_text(destination_distance_textbox, "Distance to CalTech: " + get_current_distance_from_caltech(current_location) + "m")

# Helper methods for the game
def lost(seconds):
    """Manages the lost state for the game."""
    global current_location, distance_until_turn_textbox, destination_distance_textbox

    draw_text(speed_textbox, "")
    draw_text(distance_until_turn_textbox, "")
    draw_text(destination_distance_textbox, "")
    draw_text(turn_textbox, "OH NO. WRONG TURN!")

    for x in range(0, seconds):
        draw_text(distance_until_turn_textbox, "Rerouting in " + str(10 - x) + " seconds ...")
        draw_text(destination_distance_textbox, "Distance to CalTech: ??? m")
        update_display()
        pygame.time.wait(1000)
    change_location(current_location.left_link)
    draw_text(turn_textbox, "")
    update_display()

def handle_turn(turn):
    """Handles the turn after the player has input an action."""
    global current_location, distance_until_turn, turn_textbox, LEFT_BUTTON_LED, RIGHT_BUTTON_LED

    turnLED = LEFT_BUTTON_LED
    notTurnLED = RIGHT_BUTTON_LED
    if(turn == "right"):
        turnLED = RIGHT_BUTTON_LED
        notTurnLED = LEFT_BUTTON_LED

    GPIO.output(notTurnLED, False)

    flash_text(turn_textbox, "TURNING " + turn.upper(), LED=turnLED)
    SCREEN.fill(BLACK)
    pygame.display.flip()
    pygame.time.wait(250)
    GPIO.output(turnLED, False)
    new_location = getattr(current_location, turn + "_link")
    change_location(new_location)
    draw_all_stats()
    draw_text(turn_textbox, '')
    update_display()
    print "Turned " + turn + ". new location is " + current_location.name
    distance_until_turn = current_location.distance

def get_turn():
    """Get the turn from the player action"""
    draw_text(choose_textbox, "TIME TO TURN!")
    GPIO.output(LEFT_BUTTON_LED, True)
    GPIO.output(RIGHT_BUTTON_LED, True)

    turn_text = ""

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.QUIT
            if event.type == USEREVENT:
                if event.action == 'LEFT_TURN':
                    handle_turn("left")
                    return
                elif event.action == 'RIGHT_TURN':
                    handle_turn("right")
                    return

        draw_text(direction_textbox, turn_text)
        update_display()
        if turn_text:
            turn_text = ""
        else:
            turn_text = "LEFT OR RIGHT?"
        pygame.time.wait(500)s

# Initializations
print "Rendering welcome screen..."
welcome_textbox = TextBox(0, 0, SCREENWIDTH, SCREENHEIGHT, BLACK)
draw_text(welcome_textbox, "CANNONBALL RUN: The Game", WHITE)
update_display()

print "Conducting remaining initializations..."

print "Initializing GPIO ports and callbacks..."
# GPIO port declarations
os.chdir("/home/pi/Hacker/")
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LEFT_BUTTON_INPUT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LEFT_BUTTON_LED, GPIO.OUT)
GPIO.setup(RIGHT_BUTTON_INPUT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RIGHT_BUTTON_LED, GPIO.OUT)
GPIO.setup(SPEEDOMETER, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# GPIO port callback definitions
GPIO.add_event_detect(SPEEDOMETER, GPIO.RISING callback=update_speedometer_tick, bouncetime=500)
GPIO.add_event_detect(LEFT_BUTTON_INPUT, GPIO.FALLING, callback=left_button, bouncetime=500)
GPIO.add_event_detect(RIGHT_BUTTON_INPUT, GPIO.FALLING, callback=right_button, bouncetime=500)

# Locations
print "Initializing Locations..."
location_dict = {
    "highway_a":Location("highway-a-full.png"),
    "highway_b":Location("highway-b-full.png"),
    "highway_c":Location("highway-c-full.png"),
    "highway_d":Location("highway-d-full.png"),
    "highway_e":Location("highway-e-full.png"),
    "highway_f":Location("highway-f-full.png"),
    "highway_g":Location("highway-g-full.png"),
    "highway_h":Location("highway-h-full.png"),
    "highway_i":Location("highway-i-full.png"),
    "highway_j":Location("highway-j-full.png"),
    "calTech":Location("CalTech.jpg"),
    "lost_highway_a":Location("lost-highway-a.jpg"),
    "lost_highway_b":Location("lost-highway-b.jpg"),
    "lost_highway_c":Location("lost-highway-c.jpg"),
    "lost_highway_d":Location("lost-highway-d.jpg"),
    "lost_highway_e":Location("lost-highway-e.png"),
    "lost_highway_f":Location("lost-highway-f.png"),
    "lost_highway_g":Location("lost-highway-g.png")
}

print "Initializing map..."
## To correctly navigate from beginning to end:
# A: left
# B: right
# C: right
# D: left
# E: left
# F: right
# G: left
# H: right
# I: right
# J: left
location_dict["highway_a"].left_link = "highway_b"
location_dict["highway_a"].right_link = "lost_highway_a"

location_dict["highway_b"].left_link = "lost_highway_a"
location_dict["highway_b"].right_link = "highway_c"

location_dict["highway_c"].left_link = "lost_highway_a"
location_dict["highway_c"].right_link = "highway_d"

location_dict["highway_d"].left_link = "highway_e"
location_dict["highway_d"].right_link = "lost_highway_b"

location_dict["highway_e"].left_link = "highway_f"
location_dict["highway_e"].right_link = "lost_highway_c"

location_dict["highway_f"].left_link = "lost_highway_d"
location_dict["highway_f"].right_link = "highway_g"

location_dict["highway_g"].left_link = "highway_h"
location_dict["highway_g"].right_link = "lost_highway_e"

location_dict["highway_h"].left_link = "lost_highway_f"
location_dict["highway_h"].right_link = "highway_i"

location_dict["highway_i"].left_link = "lost_highway_g"
location_dict["highway_i"].right_link = "highway_j"

location_dict["highway_j"].left_link = "calTech"
location_dict["highway_j"].right_link = "lost_highway_g"

location_dict["lost_highway_a"].left_link = "highway_a"
location_dict["lost_highway_a"].right_link = "highway_a"

location_dict["lost_highway_b"].left_link = "highway_b"
location_dict["lost_highway_b"].right_link = "highway_b"

location_dict["lost_highway_c"].left_link = "highway_c"
location_dict["lost_highway_c"].right_link = "highway_c"

location_dict["lost_highway_d"].left_link = "highway_d"
location_dict["lost_highway_d"].right_link = "highway_d"

location_dict["lost_highway_e"].left_link = "highway_e"
location_dict["lost_highway_e"].right_link = "highway_e"

location_dict["lost_highway_f"].left_link = "highway_f"
location_dict["lost_highway_f"].right_link = "highway_f"

location_dict["lost_highway_g"].left_link = "highway_g"
location_dict["lost_highway_g"].right_link = "highway_g"

print "Calculating map distances..."
for k, v in location_dict.iteritems():
    v.distance_to_caltech = get_distance_to_caltech(v)

print "Initializing HUD..."
# Defined values for the sizes of the textboxes in the HUD

TEXTBOX_WIDTH  = SCREENWIDTH/3
TEXTBOX_HEIGHT = SCREENHEIGHT/6
TEXTBOX_TOP    = SCREENHEIGHT - TEXTBOX_HEIGHT*1.5

speed_textbox = TextBox(
    0,
    TEXTBOX_TOP,
    TEXTBOX_WIDTH,
    TEXTBOX_HEIGHT/2)
distance_until_turn_textbox = TextBox(
    0,
    TEXTBOX_TOP + TEXTBOX_HEIGHT/2,
    TEXTBOX_WIDTH,
    TEXTBOX_HEIGHT/2)
turn_textbox = TextBox(
    TEXTBOX_WIDTH,
    TEXTBOX_TOP,
    TEXTBOX_WIDTH,
    TEXTBOX_HEIGHT)
destination_distance_textbox = TextBox(
    TEXTBOX_WIDTH*2,
    TEXTBOX_TOP,
    TEXTBOX_WIDTH,
    TEXTBOX_HEIGHT)

# These textboxes are only drawn when it comes time to choose a turn direction.
choose_textbox = TextBox(
    TEXTBOX_WIDTH,
    TEXTBOX_TOP,
    TEXTBOX_WIDTH,
    TEXTBOX_HEIGHT/2
)
direction_textbox = TextBox(
    TEXTBOX_WIDTH,
    TEXTBOX_TOP + TEXTBOX_HEIGHT/2,
    TEXTBOX_WIDTH,
    TEXTBOX_HEIGHT/2
)

print "Initialization complete!"

def welcome():
    """Enable our users to play CANNONBALL: THE GAME"""
    global SCREENWIDTH, SCREENHEIGHT, BLACK, WHITE, current_speed, current_location, turn_textbox, distance_until_turn
    instruction_textbox = TextBox(
        0,
        0,
        SCREENWIDTH,
        SCREENHEIGHT/3,
        BLACK
    )
    message_textbox = TextBox(
        0,
        SCREENHEIGHT/3,
        SCREENWIDTH,
        SCREENHEIGHT/3,
        BLACK
    )
    welcome_speed_textbox = TextBox(
        0,
        SCREENHEIGHT/3 * 2,
        SCREENWIDTH,
        SCREENHEIGHT/3,
        BLACK
    )

    SCREEN.fill(BLACK)
    pygame.display.flip()
    flash_text(instruction_textbox, "Pedal to Start!", 500, WHITE)

    draw_text(instruction_textbox, "Pedal to Start!", WHITE)
    draw_text(message_textbox, "Getting up to speed...", WHITE)
    draw_text(welcome_speed_textbox, "Speed: " + str(current_speed) + " m/s", WHITE)
    update_display()

    for x in range(0, 10):
        current_speed = get_current_speed()
        draw_text(welcome_speed_textbox, "")
        draw_text(welcome_speed_textbox, "Speed: " + str(current_speed) + " m/s", WHITE)
        if x > 6:
            draw_text(message_textbox, "")
            draw_text(message_textbox, "Starting in " + str(10 - x) + " . . .", WHITE)
        update_display()
        pygame.time.wait(1000)

    change_location(current_location)
    distance_until_turn = current_location.distance
    draw_all_stats()
    draw_text(turn_textbox, "")
    update_display()

def main_game():
    """Main game"""
    global current_location
    global current_speed
    global distance_until_turn

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        ## If we're at CalTech, get out of the main game loop.
        if current_location.name == "CalTech":
            return

        ## If we're lost, iterate through the lost loop for x seconds.
        ## Then advance to the next iteration of the game loop.
        if current_location.name.find("lost") > -1:
            lost(10)
            CLOCK.tick(FPS)
            continue

        ## If we've covered the distance for this location, get the turn.
        ## Then advance to the next iteration of the game loop.
        if distance_until_turn == 0:
            get_turn()
            CLOCK.tick(FPS)
            continue

        ## If we haven't gotten to the turn yet, update our stats.
        current_speed = get_current_speed()
        incremental_distance = get_incremental_distance()

        if distance_until_turn - incremental_distance < 0:
            distance_until_turn = 0
        else:
            distance_until_turn -= incremental_distance
        draw_all_stats()

        ## If we're getting close to our turn, say so.
        if distance_until_turn < (0.1 * current_location.distance):
            draw_text(turn_textbox, "TURN UPCOMING")

        update_display()
        CLOCK.tick(FPS)

def success():
    """Do the stuff we do once we're at CalTech"""
    global speed_textbox, distance_until_turn_textbox, destination_distance_textbox
    draw_text(speed_textbox, "")
    draw_text(distance_until_turn_textbox, "")
    draw_text(turn_textbox, "YOU MADE IT!")
    draw_text(destination_distance_textbox, "")
    update_display()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        CLOCK.tick(FPS)

welcome()
main_game()
success()
