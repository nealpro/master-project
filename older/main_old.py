# This code belongs to Team 3 of FSE100 class of Fall 2023.

import RPi.GPIO as GPIO
import time
import board
import adafruit_tcs34725

# Ultrasonic sensor pins
TRIG = 11
ECHO = 12

# Buzzer pin
BUZZER = 35

# Vibration motor pin
# VIB_MOTOR = 37  # GPIO 26

# RGB sensor setup
i2c = board.I2C()
sensor = adafruit_tcs34725.TCS34725(i2c)
sensor.integration_time = 50
sensor.gain = 4

# Define the motor state
MOTOR_STATE = False

# Set up the GPIO pins for the ultrasonic sensor, the buzzer, and the vibration motor
def setup():
    # Vibration motor setup
    GPIO.setup(37, GPIO.OUT)
    # Vib = GPIO.PWM(VIB_MOTOR, 50) # This function is used to create a PWM instance.
    # Vib.start(50)
    global Buzz  # Define Buzz as a global variable
    # global Vib
    GPIO.cleanup() # As long as there are no other scripts running, this line can be run.
    # GPIO.setmode(GPIO.BOARD)

    # Ultrasonic sensor setup
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)

    # Buzzer setup
    GPIO.setup(BUZZER, GPIO.OUT)
    Buzz = GPIO.PWM(BUZZER, 440)
    Buzz.start(50)

def distance():
    print("Measuring distance...")
    GPIO.output(TRIG, False)
    time.sleep(0.000002)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    pulse_start = time.time()
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        if time.time() - pulse_start > 0.01:  # Just to prevent an infinite loop
            print("Echo pulse not received - start")
            return -1

    pulse_end = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        if time.time() - pulse_end > 0.01:  # Just to prevent an infinite loop
            print("Echo pulse not received - end")
            return -1

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # Speed of sound at sea level is 34300 cm/s
    distance = round(distance, 2)
    print("Measured distance: ", distance, "cm")
    return distance


def detect_red():
    # global MOTOR_STATE
    color_rgb = sensor.color_rgb_bytes
    print(f"RGB color: {color_rgb}")
    # A simple check for red color dominance
    if color_rgb[0] > 100 and color_rgb[1] < 50 and color_rgb[2] < 50:
        # if not MOTOR_STATE:
        GPIO.output(37, GPIO.HIGH) # Turn on vibration motor
        time.sleep(10)
        GPIO.output(37, GPIO.LOW)   # Turn off vibration motor
            # Vib.start(50)
            # MOTOR_STATE = True
    else:
        # if MOTOR_STATE:
        GPIO.output(37, GPIO.LOW)   # Turn off vibration motor
            # Vib.stop()
            # MOTOR_STATE = False
    time.sleep(0.5) # Delay to prevent overwhelming the RGB sensor

def loop():
    while True:
        # dis = distance()
        # print(dis, 'cm')
        # Buzz.stop()
        # # Changing frequencies
        # d = 0
        # # Activate buzzer when distance is less than 200 cm (2 meters)
        # if dis < 200:
        #     Buzz.start(75)
        #     if (d % 2) == 0:
        #         Buzz.ChangeFrequency(600)
        #     else:
        #         Buzz.ChangeFrequency(500)
        #     time.sleep(0.5)
        #     d+=1
        # else:
        #     time.sleep(0.3)
        
        # Check for the color red
        detect_red()

def destroy():
    # Vib.stop()
    Buzz.stop()
    GPIO.cleanup()

# Run the code
if __name__ == "__main__":
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()
