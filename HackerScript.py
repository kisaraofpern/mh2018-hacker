"""Hacker Island Interaction game code"""
import time
import os
import random as rand
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
SCREEN = pygame.display.set_mode((0,0))
# pygame.display.toggle_fullscreen()

## Default values for class definitions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SCREENWIDTH = SCREEN.get_width()
SCREENHEIGHT = SCREEN.get_height()

# This Rect will be used in rference to updating SCREEN
# after it has been enblittened.
MAIN_RECT = pygame.Rect(0, 0, SCREENWIDTH, SCREENHEIGHT)

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
print "Setting default values for flags..."
at_caltech = False
done = False
suppress = False
turn_time = False
turn_left = False
turn_right = False

print "Setting baseline values for dynamic variables..."
current_location = "highway_a"
distance_traveled = 0  # In meters. The amount of distance traveled whilst in the current location
current_speed = 0  # In meters/second. Calculated from the RPM of the bike
time_to_dest = 0  # In seconds. Calculated from the distance remaining and the speed
total_distance = 0 # In meters.
dirty_rects = []
speedometer_tick = 0 # In milliseconds.

print "Setting static values..."
tick_time = 1000  #In milliseconds. Sets the framerate of the game

# Functions
# Callbacks for user actions
def left_button(input):
    global suppress
    global turn_left

    if not suppress:
        print "Left button press detected"
        turn_left = True
        suppress = True

def right_button(input):
    global suppress
    global turn_right

    if not suppress:
        print "Right button press detected"
        turn_right = True
        suppress = True

def quit_button(input):
    print "Quit button detected! \n Quitting..."
    pygame.quit()
    GPIO.cleanup()

def update_speedometer_tick(input):
    global speedometer_tick

    print "speedometer tick detected!"
    speedometer_tick = CLOCK.tick()
    print(str(speedometer_tick)+" milliseconds since last tick...")

# Resets
def reset_flags():
    global suppress, turn_left, turn_right, turn_time
    suppress = False
    turn_left = False
    turn_right = False
    turn_time = False

def reset_values():
    global distance_traveled
    distance_traveled = 0

# Calculations
def get_current_speed():
    pedal_circumference = 2
    # return = pedal_circumference/(speedometer_tick/1000)
    return rand.randrange(4, 8)

def get_incremental_distance():
    # Distance traveled since last tick,
    # using a linear interpolation based on previous speed and current speed
    if time_to_dest == 0:
        return 0
    else:
        return ((current_speed+get_current_speed())/2)*(tick_time/1000)

def get_distance_to_caltech(location):
    if location.name == "CalTech":
        return 0

    if location.name == "highway_j_full":
        return location.distance
    else:
        child_location = location_dict[location.left_link]
        if location.left_link.find("lost") > -1:
            child_location = location_dict[location.right_link]
        return location.distance + get_distance_to_caltech(child_location)

# Transformations
def change_location(location):
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
    global dirty_rects
    pygame.display.update(dirty_rects)
    dirty_rects = []

def flash_text(textbox, string, text_color=BLACK, font="Piboto", font_size=40):
    """Flashes the text in the display three times"""
    for x in range (0, 3):
        draw_text(textbox, string, text_color, font, font_size)
        update_display()
        pygame.time.wait(250)

def draw_all_stats():
    draw_text(speed_textbox, "Speed: " + str(current_speed) + " m/s")
    draw_text(total_dist_textbox, "Total Distance Traveled: " + str(total_distance) + "m")
    draw_text(destination_distance_textbox, "Distance to CalTech: " + str(get_distance_to_caltech(current_location)) + "m")

# Initializations
print "Conducting remaining initializations..."

print "Initializing GPIO ports and callbacks..."
# GPIO port declarations
os.chdir("/home/pi/Hacker/")
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  #Right button input
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)  #Speedometer input
GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Left button input
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Quit button input

# GPIO port callback definitions
GPIO.add_event_detect(16, GPIO.FALLING, callback=quit_button, bouncetime=500)  #Quit button input
GPIO.add_event_detect(13, GPIO.RISING, callback=update_speedometer_tick, bouncetime=500)  #Speedometer input
GPIO.add_event_detect(11, GPIO.RISING, callback=right_button, bouncetime=500)  #Right button input
GPIO.add_event_detect(15, GPIO.RISING, callback=left_button, bouncetime=500)   #Left button input

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

print "Initializing HUD..."
# Defined values for the sizes of the textboxes in the HUD

print SCREENHEIGHT
TEXTBOX_WIDTH  = SCREENWIDTH/3
TEXTBOX_HEIGHT = SCREENHEIGHT/6
TEXTBOX_TOP    = SCREENHEIGHT - TEXTBOX_HEIGHT*1.5

print TEXTBOX_TOP
print TEXTBOX_HEIGHT
print TEXTBOX_TOP+TEXTBOX_HEIGHT/2
print TEXTBOX_TOP+TEXTBOX_HEIGHT

speed_textbox = TextBox(
    0,
    TEXTBOX_TOP,
    TEXTBOX_WIDTH,
    TEXTBOX_HEIGHT/2)
total_dist_textbox = TextBox(
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

change_location(current_location)
draw_all_stats()
draw_text(turn_textbox, "")
update_display()

pygame.time.set_timer(pygame.USEREVENT, tick_time)
print "Initialization complete!"

##Pygame runtime
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        if event.type == pygame.USEREVENT:
            incremental_distance = get_incremental_distance()
            total_distance += incremental_distance
            draw_all_stats()
            update_display()

            if current_location.name == "CalTech":
                draw_text(turn_textbox, "YOU'VE MADE IT!")
                update_display()
                at_caltech = True

            if not turn_time and not at_caltech:
                distance_traveled += incremental_distance

                if distance_traveled >= current_location.distance:  #If there is no more distance left, set turn_time to True
                    turn_time = True
                    draw_text(turn_textbox, "LEFT OR RIGHT?")
                    update_display()
                    print("Time to turn! " + str(turn_time))

                current_speed = get_current_speed()  #Update current speed from RPM

                time_to_dest = 0

                if current_location.distance > distance_traveled:
                    time_to_dest = ((float(current_location.distance) - float(distance_traveled))/float(current_speed))

                if distance_traveled > (0.9 * current_location.distance) and not turn_time:
                    draw_text(turn_textbox, "TURN UPCOMING")
                    update_display()

                if turn_left:
                    reset_flags()
                if turn_right:
                    reset_flags()

            if turn_time and not at_caltech:
                print("Turning time! " + str(turn_time))
                if turn_left:
                    flash_text(turn_textbox, "LEFT TURN")
                    draw_text(turn_textbox, '')
                    change_location(current_location.left_link)
                    update_display()
                    print "\nTurned left. New location is "+current_location.name
                    #time.sleep(.25)
                    reset_flags()
                    reset_values()

                if turn_right:
                    flash_text(turn_textbox, "RIGHT TURN")
                    draw_text(turn_textbox, '')
                    change_location(current_location.right_link)
                    update_display()
                    print "\nTurned right. New location is "+current_location.name
                    #time.sleep(.25)
                    reset_flags()
                    reset_values()
