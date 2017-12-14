"""Pygame testbed"""
import pygame
from pygame.locals import *
import RPi.GPIO as GPIO
import time

SPEEDOMETER = 18

def update_speedometer_tick(input):
    print 'BOOOOOOOP'

GPIO.setmode(GPIO.BOARD)
GPIO.setup(SPEEDOMETER, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(SPEEDOMETER, GPIO.FALLING, callback=update_speedometer_tick, bouncetime=1)

while True:
    print 'beep'
    time.sleep(1)
    
