import numpy as np
import RPi.GPIO as GPIO
import time
import pygame
import os
import random as rand

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
default_distance = 100

class location():
    def __init__(self, image, distance=default_distance):
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (1920, 1080))
        self.leftLink = "0"
        self.rightLink = "0"
        self.distance = distance
        self.name = image.split(".")[0]
    def convertImage(self):
        self.image = self.image.convert()

##Location initializations
locationDict = {
    "highway_a":location("highway-a.png"),
    "highway_b":location("highway-b.png"),
    "highway_c":location("highway-c.png"),
    "highway_d":location("highway-d.png"),
    "highway_e":location("highway-e.png"),
    "highway_f":location("highway-f.png"),
    "highway_g":location("highway-g.png"),
    "highway_h":location("highway-h.png"),
    "highway_i":location("highway-i.png"),
    "highway_j":location("highway-j.png"),
    "calTech":location("CalTech.jpg"),
    "lost_highway_a":location("lost-highway-a.jpg"),
    "lost_highway_b":location("lost-highway-b.jpg"),
    "lost_highway_c":location("lost-highway-c.jpg"),
    "lost_highway_d":location("lost-highway-d.jpg"),
    "lost_highway_e":location("lost-highway-e.png"),
    "lost_highway_f":location("lost-highway-f.png"),
    "lost_highway_g":location("lost-highway-g.png")
}

print "Images loaded..."

##Tree linkages
locationDict["highway_a"].leftLink = "highway_b"
locationDict["highway_a"].rightLink = "lost_highway_a"

locationDict["highway_b"].leftLink = "highway_c"
locationDict["highway_b"].rightLink = "lost_highway_a"

locationDict["highway_c"].leftLink = "highway_d"
locationDict["highway_c"].rightLink = "lost_highway_a"

locationDict["highway_d"].leftLink = "highway_e"
locationDict["highway_d"].rightLink = "lost_highway_b"

locationDict["highway_e"].leftLink = "highway_f"
locationDict["highway_e"].rightLink = "lost_highway_c"

locationDict["highway_f"].leftLink = "highway_g"
locationDict["highway_f"].rightLink = "lost_highway_d"

locationDict["highway_g"].leftLink = "highway_h"
locationDict["highway_g"].rightLink = "lost_highway_e"

locationDict["highway_h"].leftLink = "highway_i"
locationDict["highway_h"].rightLink = "lost_highway_f"

locationDict["highway_i"].leftLink = "highway_j"
locationDict["highway_i"].rightLink = "lost_highway_g"

locationDict["highway_j"].leftLink = "calTech"
locationDict["highway_j"].rightLink = "lost_highway_g"

locationDict["lost_highway_a"].leftLink = "highway_a"
locationDict["lost_highway_a"].rightLink = "highway_a"

locationDict["lost_highway_b"].leftLink = "highway_b"
locationDict["lost_highway_b"].rightLink = "highway_b"

locationDict["lost_highway_c"].leftLink = "highway_c"
locationDict["lost_highway_c"].rightLink = "highway_c"

locationDict["lost_highway_d"].leftLink = "highway_d"
locationDict["lost_highway_d"].rightLink = "highway_d"

locationDict["lost_highway_e"].leftLink = "highway_e"
locationDict["lost_highway_e"].rightLink = "highway_e"

locationDict["lost_highway_f"].leftLink = "highway_f"
locationDict["lost_highway_f"].rightLink = "highway_f"

locationDict["lost_highway_g"].leftLink = "highway_g"
locationDict["lost_highway_g"].rightLink = "highway_g"

print "Tree links created..."

##Tree initialization
currentLocation = "highway_a"

#Functions
def quitButton(input):
    print "Quit button detected! \n Quitting..."
    pygame.quit()
    GPIO.cleanup()

def changeLocation(location):
    global currentLocation
    currentLocation = locationDict[location]
    screen.fill((255, 255, 255))
    screen.blit(currentLocation.image, (0, 0))
    pygame.display.flip()

def leftButton(input):
    global suppress
    global turnLeft

    if suppress == False:
        print "Left button press detected\n"
        turnLeft = True
        suppress = True

def rightButton(input):
    global suppress
    global turnRight

    if suppress == False:
        print "Right button press detected\n"
        turnRight = True
        suppress = True

def resetFlags():
    global suppress
    global turnLeft
    global turnRight
    suppress = False
    turnLeft = False
    turnRight = False

def resetValues():
    global distanceTraveled
    distanceTraveled = 0

def writeText(text, xPos, yPos, color):
    global currentLocation
    screen.fill((255, 255, 255))
    screen.blit(currentLocation.image(0, 0))
    screen.blit(myfont.render(text, False, color, (xPos, yPos)))
    pygame.display.flip()

def getCurrentSpeed():
    return rand.randrange(4, 8) #Placeholder until speed driver is written

##GPIO callback event initializations
GPIO.add_event_detect(16, GPIO.FALLING, callback=quitButton, bouncetime=500)
GPIO.add_event_detect(11, GPIO.RISING, callback=rightButton, bouncetime=500)
GPIO.add_event_detect(15, GPIO.RISING, callback=leftButton, bouncetime=500)
print "GPIO callbacks set..."

##Pygame initialization
pygame.init()
print "Pygame initialized..."

##Clock initialization
clock = pygame.time.Clock()
print "Pygame clock initialized..."

##Font initialization
pygame.font.init()
myfont = pygame.font.SysFont("Times New Roman", 200)

##Initialize Pygame screen
screen = pygame.display.set_mode((0, 0))
#pygame.display.toggle_fullscreen()
print "Pygame screen initialization complete..."

##Convert images for Pygame display
for x in locationDict.keys():
    locationDict[x].convertImage()
print "Images converted..."

##Set flags
done = False
turnTime = False
turnLeft = False
turnRight = False
suppress = False
print "Flags and values set..."

##Set tracked values
distanceTraveled = 0  #In meters.  The amount of distance traveled in the current location
currentSpeed = 6  #In meters/second.  Calculated from the RPM of the bike
timeToDest = 0  #In seconds.  Calculated from the distance remaining and the speed
print "Tracked values set..."

##Static values
tickTime = 1000  #In milliseconds.  Sets the framrate of the game
print "Static values set..."

changeLocation(currentLocation)
pygame.time.set_timer(pygame.USEREVENT, tickTime)
print "Initialization complete!"

##Pygame runtime
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        if event.type == pygame.USEREVENT:
            print "tick"
            if turnTime == False:
                distanceTraveled += ((currentSpeed+getCurrentSpeed())/2)*(tickTime/1000)  #Add distance traveled since last tick, using a linear interpolation based on previous speed and current speed

                if distanceTraveled >= currentLocation.distance:  #If there is no more distance left, set turnTime to True
                    turnTime = True

                currentSpeed = getCurrentSpeed()  #Update current speed from RPM

                if currentLocation.distance > distanceTraveled:
                    timeToDest = ((currentLocation.distance - distanceTraveled)/currentSpeed)  #Distance remaining/speed in seconds.  Updates current ETA
                else:
                    timeToDest = 0


            if turnTime == True:
                if turnLeft == True:
                    changeLocation(currentLocation.leftLink)
                    print "\nTurned left. New location is "+currentLocation.name
                    time.sleep(.25)
                    resetFlags()

                if turnRight == True:
                    changeLocation(currentLocation.rightLink)
                    print("\nTurned right. New location is "+currentLocation.name)
                    time.sleep(.25)
                    resetFlags()
