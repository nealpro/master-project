"""
This code belongs to Team 3 of FSE100 class of Fall 2023.
"""

import RPi.GPIO as GPIO
import time
import board
import adafruit_tcs34725

# Ultrasonic sensor pins
TRIG: int = 11
ECHO: int = 12

# Buzzer pin
BUZZER: int = 35

# Vibration motor pin
VIB_MOTOR: int = 37  # GPIO 26

# RGB sensor setup
i2c = board.I2C()
sensor = adafruit_tcs34725.TCS34725(i2c)
sensor.integration_time = 50
sensor.gain = 4

# Define the motor state
MOTOR_STATE = False

# Set up the GPIO pins for the ultrasonic sensor, the buzzer, and the vibration motor
def setup():
    """
    Setup pins for the ultrasonic sensor, the buzzer, and the vibration motor.
    """
    global Buzz  # Define Buzz as a global variable
    GPIO.cleanup() # As long as there are no other scripts running, this line can be run.
    GPIO.setmode(GPIO.BOARD)

    # Ultrasonic sensor setup
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)

    # Buzzer setup
    GPIO.setup(BUZZER, GPIO.OUT)
    Buzz = GPIO.PWM(BUZZER, 440)
    Buzz.start(50)

    # Vibration motor setup
    GPIO.setup(VIB_MOTOR, GPIO.OUT)

def distance():
    print("Measuring distance...")
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

def detect_red():
    """
    Detect if the color sensed is red and activate the vibration motor.
    """
    global MOTOR_STATE
    color_rgb = sensor.color_rgb_bytes
    print(f"RGB color: {color_rgb}")
    # A simple check for red color dominance
    if color_rgb[0] > 100 and color_rgb[1] < 50 and color_rgb[2] < 50:
        if not MOTOR_STATE:
            GPIO.output(VIB_MOTOR, GPIO.HIGH)  # Turn on vibration motor
            MOTOR_STATE = True
    else:
        if MOTOR_STATE:
            GPIO.output(VIB_MOTOR, GPIO.LOW)   # Turn off vibration motor
            MOTOR_STATE = False

def loop():
    """Main loop"""
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
        
        # Check for the color red
        detect_red()
        time.sleep(1)  # Delay to prevent overwhelming the RGB sensor

def destroy():
    """Destroy the GPIO pins on exit."""
    Buzz.stop()
    GPIO.cleanup()

# Run the code
if __name__ == "__main__":
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()
