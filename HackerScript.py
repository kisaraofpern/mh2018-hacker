import numpy as np
import RPi.GPIO as GPIO
import time
import pygame
import os
import random as rand

print("Initializing...")

##GPIO port declarations
os.chdir("/home/pi/Hacker/")
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
print("GPIO ports initialized...")

##GPIO port initial states
GPIO.output(13, True)

##Class definitions
class location():
    def __init__(self, image, distance):
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image,(1920,1080))
        self.leftLink = "0"
        self.rightLink = "0"
        self.distance = distance
        self.name = image.split(".")[0]
    def convertImage(self):
        self.image = self.image.convert()

##Location initializations
locationDict = {"TIEfo":location("TIEfo.jpg",100)
                ,"TIEadv":location("TIEadv.jpg",100)
                ,"TIE":location("TIE.jpg",100)}
print("Images loaded...")

##Tree linkages
locationDict["TIEfo"].leftLink = "TIEadv"
locationDict["TIEfo"].rightLink = "TIE"

locationDict["TIE"].leftLink = "TIEadv"
locationDict["TIE"].rightLink = "TIEfo"

locationDict["TIEadv"].leftLink = "TIEfo"
locationDict["TIEadv"].rightLink = "TIE"
print("Tree links created...")

##Tree initialization
currentLocation = "TIEfo"

#Functions
def quitButton(input):
    print("Quit button detected! \n Quitting...")
    pygame.quit()
    GPIO.cleanup()

def changeLocation(location):
    global currentLocation
    currentLocation = locationDict[location]
    screen.fill((255,255,255))
    screen.blit(currentLocation.image,(0,0))
    pygame.display.flip()

def leftButton(input):
    global suppress
    global turnLeft

    if suppress == False:
        print("Left button press detected\n")
        turnLeft = True
        suppress = True

def rightButton(input):
    global suppress
    global turnRight

    if suppress == False:
        print("Right button press detected\n")
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

def writeText(text,xPos,yPos,color):
    global currentLocation
    screen.fill((255,255,255))
    screen.blit(currentLocation.image(0,0))
    screen.blit(myfont.render(text, False, color, (xPos,yPos)))
    pygame.display.flip()

def getCurrentSpeed():
    return rand.randbetween(4,8) #Placeholder until speed driver is written


##GPIO callback event initializations
GPIO.add_event_detect(16, GPIO.FALLING, callback=quitButton, bouncetime=500)
GPIO.add_event_detect(11, GPIO.RISING, callback=rightButton, bouncetime=500)
GPIO.add_event_detect(15, GPIO.RISING, callback=leftButton, bouncetime=500)
print("GPIO callbacks set...")

##Pygame initialization
pygame.init()
print("Pygame initialized...")

##Clock initialization
clock = pygame.time.Clock()
print("Pygame clock initialized...")

##Font initialization
pygame.font.init()
myfont = pygame.font.SysFont("Times New Roman", 200)

##Initialize Pygame screen
screen = pygame.display.set_mode((0,0))
#pygame.display.toggle_fullscreen()
print("Pygame screen initialization complete...")

##Convert images for Pygame display
for x in locationDict.keys():
    locationDict[x].convertImage()
print("Images converted...")

##Set flags
done = False
turnTime = False
turnLeft = False
turnRight = False
suppress = False
print("Flags and values set...")

##Set tracked values
distanceTraveled = 0  #In meters.  The amount of distance traveled in the current location
currentSpeed = 6  #In meters/second.  Calculated from the RPM of the bike
timeToDest = 0  #In seconds.  Calculated from the distance remaining and the speed
print("Tracked values set...")

##Static values
tickTime = 1000  #In milliseconds.  Sets the framrate of the game
print("Static values set...")

changeLocation(currentLocation)
pygame.time.set_timer(pygame.USEREVENT, tickTime)
print("Initialization complete!")

##Pygame runtime
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        if event.type == pygame.USEREVENT:
            print("tick")
            if turnTime == False:
                distanceTraveled += ((currentSpeed+getCurrentSpeed())/2)*(tickTime/1000)  #Add distance traveled since last tick, using a linear interpolation based on previous speed and current speed
                if distanceTraveled >= currentLocation.distance:
                    turnTime = True
                currentSpeed = getCurrentSpeed()  #Update current speed from RPM
                timeToDest = ((currentLocation.distance - distanceTraveled)/currentSpeed)  #Distance remaining/speed in seconds.  Updates current ETA

            if turnTime == True:
                if turnLeft == True:
                    changeLocation(currentLocation.leftLink)
                    print("\nTurned left. New location is "+currentLocation.name)
                    time.sleep(.25)
                    resetFlags()

                if turnRight == True:
                    changeLocation(currentLocation.rightLink)
                    print("\nTurned right. New location is "+currentLocation.name)
                    time.sleep(.25)
                    resetFlags()
