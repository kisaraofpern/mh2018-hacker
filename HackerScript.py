import time
import os
import random as rand
import RPi.GPIO as GPIO
import pygame
from pygame.locals import *

print "Initializing..."

##GPIO port declarations
os.chdir("/home/pi/Hacker/")
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
print "GPIO ports initialized..."

##GPIO port initial states
GPIO.output(13, True)

## Class definitions
## Default value in meters for "how long" this location is.
DEFAULTDISTANCE = 100

class Location(object):
    def __init__(self, image, distance=DEFAULTDISTANCE):
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (1920, 1080))
        self.left_link = "0"
        self.right_link = "0"
        self.distance = distance
        self.name = image.split(".")[0]

    def convert_image(self):
        self.image = self.image.convert()

##Location initializations
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

print "Images loaded..."

## Tree linkages
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

print "Tree links created..."

##Tree initialization
current_location = "highway_a"

#Functions
def quit_button(input):
    print "Quit button detected! \n Quitting..."
    pygame.quit()
    GPIO.cleanup()

def change_location(location):
    global current_location
    current_location = location_dict[location]
    screen.fill((255, 255, 255))
    screen.blit(current_location.image, (0, 0))
    pygame.display.flip()

def left_button(input):
    global suppress
    global turn_left

    if not suppress:
        print "Left button press detected\n"
        turn_left = True
        suppress = True

def right_button(input):
    global suppress
    global turn_right

    if not suppress:
        print "Right button press detected\n"
        turn_right = True
        suppress = True

def reset_flags():
    global suppress
    global turn_left
    global turn_right
    global turn_time
    suppress = False
    turn_left = False
    turn_right = False
    turn_time = False

def reset_values():
    global distance_traveled
    distance_traveled = 0

def write_text(text, xPos, yPos, color):
    global current_location
    screen.fill((255, 255, 255))
    screen.blit(current_location.image,(0, 0))
    screen.blit(myfont.render(text, False, color),(xPos, yPos))
    pygame.display.flip()

def get_current_speed():
    return rand.randrange(4, 8) #Placeholder until speed driver is written

##GPIO callback event initializations
GPIO.add_event_detect(16, GPIO.FALLING, callback=quit_button, bouncetime=500)
GPIO.add_event_detect(11, GPIO.RISING, callback=right_button, bouncetime=500)
GPIO.add_event_detect(15, GPIO.RISING, callback=left_button, bouncetime=500)
print "GPIO callbacks set..."

##Pygame initialization
pygame.init()
print "Pygame initialized..."

##Clock initialization
clock = pygame.time.Clock()
print "Pygame clock initialized..."

##Font initialization
pygame.font.init()
myfont = pygame.font.SysFont("Times New Roman", 72)

##Initialize Pygame screen
screen = pygame.display.set_mode((0, 0))
#pygame.display.toggle_fullscreen()
print "Pygame screen initialization complete..."

##Convert images for Pygame display
for x in location_dict.keys():
    location_dict[x].convert_image()
print "Images converted..."

##Set flags
done = False
turn_time = False
turn_left = False
turn_right = False
suppress = False
print "Flags and values set..."

##Set tracked values
distance_traveled = 0  #In meters.  The amount of distance traveled in the current location
current_speed = 6  #In meters/second.  Calculated from the RPM of the bike
time_to_dest = 0  #In seconds.  Calculated from the distance remaining and the speed
print "Tracked values set..."

##Static values
tick_time = 1000  #In milliseconds.  Sets the framrate of the game
print "Static values set..."

change_location(current_location)
pygame.time.set_timer(pygame.USEREVENT, tick_time)
print "Initialization complete!"

##Pygame runtime
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        if event.type == pygame.USEREVENT:
            if not turn_time:
                distance_traveled += ((current_speed+get_current_speed())/2)*(tick_time/1000)  #Add distance traveled since last tick, using a linear interpolation based on previous speed and current speed
                write_text("You have gone: " + str(distance_traveled), 100, 100, (255,0,0))
                #print("Not turning time! " + str(distance_traveled))

                if distance_traveled >= current_location.distance:  #If there is no more distance left, set turn_time to True
                    turn_time = True
                    print("Time to turn! " + str(turn_time))

                current_speed = get_current_speed()  #Update current speed from RPM

                time_to_dest = 0 #Distance remaining/speed in seconds.  Updates current ETA

                if current_location.distance > distance_traveled:
                    time_to_dest = ((current_location.distance - distance_traveled)/current_speed)

                if turn_left:
                    reset_flags()
                if turn_right:
                    reset_flags()

            if turn_time:
                print("Turning time! " + str(turn_time))
                if turn_left:
                    change_location(current_location.left_link)
                    print "\nTurned left. New location is "+current_location.name
                    #time.sleep(.25)
                    write_text("LEFT",0,0,(255,0,0))
                    reset_flags()
                    reset_values()

                if turn_right:
                    change_location(current_location.right_link)
                    print "\nTurned right. New location is "+current_location.name
                    #time.sleep(.25)
                    write_text("RIGHT",0,0,(255,0,0))
                    reset_flags()
                    reset_values()
