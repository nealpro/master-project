import RPi.GPIO as GPIO
import time
import board
import adafruit_tcs34725

# Pins configuration
ULTRASONIC_1_TRIG = 17
ULTRASONIC_1_ECHO = 27
ULTRASONIC_2_TRIG = 23
ULTRASONIC_2_ECHO = 24
RELAY_1 = 21 # Relay 1 is for ultrasonic 1
RELAY_2 = 26 # Relay 2 is for RGB sensor
BUZZER = 7 # Buzzer is for ultrasonic 2

# States
button_state = True

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
    GPIO.setup(RELAY_1, GPIO.OUT)
    GPIO.setup(RELAY_2, GPIO.OUT)
    GPIO.setup(BUZZER, GPIO.OUT)

    # PWM setup for buzzer
    Buzz = GPIO.PWM(BUZZER, 440)  # 440Hz frequency

def distance(TRIG, ECHO):
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
        dis1 = distance(ULTRASONIC_1_TRIG, ULTRASONIC_1_ECHO)
        dis2 = distance(ULTRASONIC_2_TRIG, ULTRASONIC_2_ECHO)

        print(f"Distance 1: {dis1} cm")
        print(f"Distance 2: {dis2} cm")

        if dis1 < 2:
            GPIO.output(RELAY_1, GPIO.HIGH)
            print("Relay 1 on")
        else:
            GPIO.output(RELAY_1, GPIO.LOW)
            print("Relay 1 off")
        if dis2 < 5:
            Buzz.start(50)
        else:
            Buzz.stop()

        color_rgb = sensor.color_rgb_bytes
        print(f"RGB color detected: {color_rgb}")
        if color_rgb[0] > 100 and color_rgb[1] < 50 and color_rgb[2] < 50:
            print("Red detected")
            GPIO.output(RELAY_2, GPIO.HIGH)  # Turn on vibration motor 2
            print("Vibration motor 2 turned on.")
            time.sleep(1)
        else:
            GPIO.output(RELAY_2, GPIO.LOW)  # Turn off vibration motor 2
            print("Vibration motor 2 turned off.")
            time.sleep(1)

def destroy():
    GPIO.cleanup()

if __name__ == '__main__':     # Program start from here
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()