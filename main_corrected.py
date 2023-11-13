import RPi.GPIO as GPIO
import time
import board
import adafruit_tcs34725
# import threading
# import queue

# Pins configuration
ULTRASONIC_1_TRIG = 17
ULTRASONIC_1_ECHO = 27
ULTRASONIC_2_TRIG = 23
ULTRASONIC_2_ECHO = 24
# RELAY_1 = 21 # Relay 1 is for ultrasonic 1
RELAY_2 = 26 # Relay 2 is for RGB sensor
BUZZER = 7 # Buzzer is for ultrasonic 2
BUTTON = 16 # Touch sensor to toggle system on/off

button_state = 0

print(button_state)

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
    GPIO.setup(RELAY_2, GPIO.OUT)
    GPIO.setup(BUZZER, GPIO.OUT)
    GPIO.setup(BUTTON, GPIO.IN) # pull up to high level
    # GPIO.output(RELAY_2, GPIO.HIGH)

    # PWM setup for buzzer
    Buzz = GPIO.PWM(BUZZER, 440)  # 440Hz frequency

def detect(state: bool):
    global button_state
    if state != button_state:
        if state == 1:
            print("Touch switch is currently released.")
        if state == 0:
            print("Touch switch is currently pressed.")
        button_state = not state

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
    global button_state
    while True:
        if button_state == 0:
            # dis1q = queue.Queue()
            # dis1th = threading.Thread(target=distance, args=(ULTRASONIC_1_TRIG, ULTRASONIC_1_ECHO, dis1q))
            # dis1th.start()
            # dis1th.join()
            # dis1 = dis1q.get() 

            # dis2q = queue.Queue()
            # dis2th = threading.Thread(target=distance, args=(ULTRASONIC_2_TRIG, ULTRASONIC_2_ECHO, dis2q))
            # dis2th.start()
            # dis2th.join()
            # dis2 = dis2q.get()

            dis1 = distance1()
            print(f"Distance 1: {dis1} cm")
            
            if dis1 < 50.0:
                # GPIO.output(RELAY_1, GPIO.HIGH)
                print("Relay 1 on")
            else:
                # GPIO.output(RELAY_1, GPIO.LOW)
                print("Relay 1 off")
            time.sleep(1)
            dis2 = distance2()
            print(f"Distance 2: {dis2} cm")

            if dis2 < 400.0:
                Buzz.start(50.0)
            else:
                Buzz.stop()
            time.sleep(1)
            color_rgb = sensor.color_rgb_bytes
            print(f"RGB color detected: {color_rgb}")
            if color_rgb[0] > 100 and color_rgb[1] < 50 and color_rgb[2] < 50:
                print("Red detected")
                GPIO.output(RELAY_2, GPIO.HIGH)  # Turn on vibration motor 2
                print("Vibration motor 2 turned on.")
            else:
                GPIO.output(RELAY_2, GPIO.LOW)  # Turn off vibration motor 2
                print("Vibration motor 2 turned off.")
            print("Program will now wait for a second.")
            time.sleep(1)
            print("Checking...")
            detect(GPIO.input(BUTTON))
        else:
            # GPIO.output(RELAY_1, GPIO.LOW)
            print("System turned off.")
            print("Checking...")
            detect(GPIO.input(BUTTON))
        time.sleep(2)


def destroy():
    # GPIO.output(RELAY_1, GPIO.LOW)
    GPIO.output(RELAY_2, GPIO.LOW)
    Buzz.stop()
    GPIO.cleanup()

if __name__ == '__main__':     # Program start from here
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()