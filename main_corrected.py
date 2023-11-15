import time
import board
import adafruit_tcs34725
import RPi.GPIO as GPIO
import subprocess
# import threading
# import queue

# https://github.com/numediart/MBROLA/releases/download/3.3/MBROLA-3.3.tar.gz.asc

# Pins configuration
ULTRASONIC_1_TRIG = 17
ULTRASONIC_1_ECHO = 27
ULTRASONIC_2_TRIG = 23
ULTRASONIC_2_ECHO = 24
# RELAY_1 = 21 # Relay 1 is for ultrasonic 1
RELAY = 26 # Relay 2 is for RGB sensor
TOUCH = 20 # Touch sensor to toggle system on/off
BUZZER = 21 # Buzzer is for ultrasonic 2

touch_state = 0

def setup():
    global sensor
    global Buzz
    GPIO.setmode(GPIO.BCM)
    # RGB sensor setup
    i2c = board.I2C()
    sensor = adafruit_tcs34725.TCS34725(i2c)
    sensor.integration_time = 50
    sensor.gain = 4

    # GPIO setup
    GPIO.setup(ULTRASONIC_1_TRIG, GPIO.OUT)
    GPIO.setup(ULTRASONIC_1_ECHO, GPIO.IN)
    GPIO.setup(ULTRASONIC_2_TRIG, GPIO.OUT)
    GPIO.setup(ULTRASONIC_2_ECHO, GPIO.IN)
    # GPIO.setup(RELAY_1, GPIO.OUT)
    GPIO.setup(RELAY, GPIO.OUT)
    GPIO.setup(BUZZER, GPIO.OUT)
    GPIO.setup(TOUCH, GPIO.IN, pull_up_down=GPIO.PUD_UP) # pull up to high level
    # GPIO.output(RELAY_2, GPIO.HIGH)

    # PWM setup for buzzer
    Buzz = GPIO.PWM(BUZZER, 500)  # 440Hz frequency

def detect(state: bool):
    global touch_state
    if state != touch_state:
        if state == 0:
            print("Touch switch is currently released.")
            touch_state = state
        if state == 1:
            print("Touch switch is currently pressed.")
            touch_state = state
        else:
            raise ValueError("Touch switch is currently in an unknown state.")
    print("Touch state: ", touch_state)
    print("Sleeping for one second...")
    time.sleep(1)

def distance1(TRIG = ULTRASONIC_1_TRIG, ECHO = ULTRASONIC_1_ECHO):
    GPIO.output(TRIG, 0)
    time.sleep(0.000002)

    GPIO.output(TRIG, 1)
    time.sleep(0.00001)
    GPIO.output(TRIG, 0)

    while GPIO.input(ECHO) == 0:
        a = 0
    time1 = time.time()
    while GPIO.input(ECHO) == 1:
        a = 1
    time2 = time.time()

    during = time2 - time1
    return during * 340 / 2 * 100

def distance2(TRIG = ULTRASONIC_2_TRIG, ECHO = ULTRASONIC_2_ECHO):
    GPIO.output(TRIG, 0)
    time.sleep(0.000002)

    GPIO.output(TRIG, 1)
    time.sleep(0.00001)
    GPIO.output(TRIG, 0)

    while GPIO.input(ECHO) == 0:
        a = 0
    time3 = time.time()
    while GPIO.input(ECHO) == 1:
        a = 1
    time4 = time.time()

    during = time4 - time3
    return during * 340 / 2 * 100

def loop():
    global touch_state
    while True:
        if touch_state == 0:
            dis1 = distance1()
            speak(f"Distance 1: {dis1:.2f} cm")
            print(f"Distance 1: {dis1} cm")
            dis2 = distance2()

            if dis2 < 400.0:
                print("Object detected at second ultrasonic sensor.")
                Buzz.start(90.0)
            else:
                Buzz.stop()

            print(f"Distance 2: {dis2} cm")
            time.sleep(1)
            color_rgb = sensor.color_rgb_bytes
            print(f"RGB color detected: {color_rgb}")
            if color_rgb[0] > 100 and color_rgb[1] < 50 and color_rgb[2] < 50:
                print("Red detected")
                GPIO.output(RELAY, GPIO.HIGH)  # Turn on vibration motor 2
                print("Vibration motor 2 turned on.")
            else:
                GPIO.output(RELAY, GPIO.LOW)  # Turn off vibration motor 2
                print("Vibration motor 2 turned off.")
            print("Program will now wait for a second.")
            time.sleep(1)
            print("Checking...")
            detect(GPIO.input(TOUCH))
        else:
            GPIO.output(RELAY, GPIO.LOW)
            Buzz.stop()
            print("System turned off.")
            print("Checking...")
            detect(GPIO.input(TOUCH))
        time.sleep(2) 


def destroy():
    # GPIO.output(RELAY_1, GPIO.LOW)
    GPIO.output(RELAY, GPIO.LOW)
    Buzz.stop()
    GPIO.cleanup()

def speak(content):
    p = subprocess.Popen(f"espeak-ng -v mb-en1 \"{content}\"",
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    # return iter(p.stdout.readline, b'')

if __name__ == '__main__':     # Program start from here
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()