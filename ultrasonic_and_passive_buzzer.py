#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

# Ultrasonic sensor pins
TRIG = 11
ECHO = 12

# Buzzer pin
Buzzer = 35  # TODO: Change this based on current setup

# Set up the GPIO pins for the ultrasonic sensor and the buzzer
def setup():
    GPIO.setmode(GPIO.BOARD)
    
    # Ultrasonic sensor setup
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)
    
    # Buzzer setup
    GPIO.setup(Buzzer, GPIO.OUT)
    global Buzz
    Buzz = GPIO.PWM(Buzzer, 440)
    Buzz.start(50)

def distance():
    GPIO.output(TRIG, 0)
    time.sleep(0.000002)

    GPIO.output(TRIG, 1)
    time.sleep(0.00001)
    GPIO.output(TRIG, 0)

    while GPIO.input(ECHO) == 0:
        pass
    time1 = time.time()
    
    while GPIO.input(ECHO) == 1:
        pass
    time2 = time.time()

    during = time2 - time1
    return during * 340 / 2 * 100

def loop():
    while True:
        dis = distance()
        print(dis, 'cm')
        Buzz.stop()
        # Changing frequencies
        d = 0
        # Activate buzzer when distance is less than 200 cm (2 meters)
        if dis < 200:
            Buzz.start(75)
            if (d % 2) == 0:
                Buzz.ChangeFrequency(600)
            else:
                Buzz.ChangeFrequency(500)
            time.sleep(0.5)
            d+=1
        else:
            time.sleep(0.3)

# Cleanup the GPIO pins on exit
def destroy():
    Buzz.stop()
    GPIO.cleanup()

# Run the code
if __name__ == "__main__":
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()
