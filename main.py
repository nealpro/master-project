import RPi.GPIO as GPIO
import time
import threading
import board
import adafruit_tcs34725

# Pins configuration
ULTRASONIC_1_TRIG = 17
ULTRASONIC_1_ECHO = 27
ULTRASONIC_2_TRIG = 23
ULTRASONIC_2_ECHO = 24
RELAY_1 = 21
RELAY_2 = 26
BUZZER = 7
BUTTON = 18

# Set GPIO mode
GPIO.setmode(GPIO.BCM)
# RGB sensor setup
i2c = board.I2C()  # Assuming this part works correctly since it's not GPIO related
sensor = adafruit_tcs34725.TCS34725(i2c)
sensor.integration_time = 50
sensor.gain = 4
print("RGB sensor setup complete.")
time.sleep(1)
# GPIO setup
print("Setting up GPIO pins.")
GPIO.setup(ULTRASONIC_1_TRIG, GPIO.OUT)
GPIO.setup(ULTRASONIC_1_ECHO, GPIO.IN)
GPIO.setup(ULTRASONIC_2_TRIG, GPIO.OUT)
GPIO.setup(ULTRASONIC_2_ECHO, GPIO.IN)
GPIO.setup(RELAY_1, GPIO.OUT) # Outputs can't be set to pull up or down 🤡
GPIO.setup(RELAY_2, GPIO.OUT)
GPIO.setup(BUZZER, GPIO.OUT)
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
print("GPIO pins setup complete.")

# PWM setup for buzzer
print("Setting up PWM for buzzer.")
Buzz = GPIO.PWM(BUZZER, 440)  # 440Hz frequency
print("PWM setup complete.")

def distance(trig, echo):
    print(f"Measuring distance using trig: {trig}, echo: {echo}")
    # Set Trigger to HIGH
    GPIO.output(trig, True)
    time.sleep(0.00001)  # 10us delay
    GPIO.output(trig, False)

    start_time = time.time()
    stop_time = time.time()

    # Save StartTime
    while GPIO.input(echo) == 0:
        start_time = time.time()

    # Save time of arrival
    while GPIO.input(echo) == 1:
        stop_time = time.time()

    # Time difference between start and arrival
    time_elapsed = stop_time - start_time
    # Multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (time_elapsed * 34300) / 2
    print(f"Distance measured: {distance} cm")

    return distance

def ultrasonic_sensor_loop():
    print("Ultrasonic sensor loop started.")
    while button_state:
        print("Measuring distances.")
        dist1 = distance(ULTRASONIC_1_TRIG, ULTRASONIC_1_ECHO)
        dist2 = distance(ULTRASONIC_2_TRIG, ULTRASONIC_2_ECHO)
        print(f"Distances: {dist1}, {dist2}")

        if dist1 < 200:  # less than 2 meters
            # GPIO.output(RELAY_1, GPIO.HIGH)
            print("Vibration motor 1 turned on.")
            time.sleep(0.5)
        else:
            # GPIO.output(RELAY_1, GPIO.LOW)
            print("Vibration motor 1 turned off.")
            time.sleep(0.5)

        if dist2 < 700:  # less than 7 meters
            Buzz.start(50)  # Turn on passive buzzer
            print("Passive buzzer turned on.")
            time.sleep(0.5)
        else:
            Buzz.stop()  # Turn off passive buzzer
            print("Passive buzzer turned off.")
            time.sleep(0.5)

        if (GPIO.input(BUTTON) == False):
            button_state = False
            print("Button pressed, exiting ultrasonic sensor loop.")

        time.sleep(1)
    else:
        print("Ultrasonic sensor loop stopped.")
        if (GPIO.input(BUTTON) == False):
            button_state = True
            print("Button pressed, entering ultrasonic sensor loop.")
            ultrasonic_sensor_loop()

def detect_red_loop():
    print("Red detection loop started.")
    while button_state:
        color_rgb = sensor.color_rgb_bytes
        print(f"RGB color detected: {color_rgb}")
        if color_rgb[0] > 100 and color_rgb[1] < 50 and color_rgb[2] < 50:
            print("Red detected")
            GPIO.output(RELAY_2, GPIO.HIGH)  # Turn on vibration motor 2
            print("Vibration motor 2 turned on.")
        else:
            GPIO.output(RELAY_2, GPIO.LOW)  # Turn off vibration motor 2
            print("Vibration motor 2 turned off.")

        time.sleep(0.1)
        if (GPIO.input(BUTTON) == False):
            button_state = False
            print("Button pressed, exiting red detection loop.")
    else:
        print("Red detection loop stopped.")
        if (GPIO.input(BUTTON) == False):
            button_state = True
            print("Button pressed, entering red detection loop.")
            ultrasonic_sensor_loop()

def main():
    print("Main function started.")
    try:
        # Threads setup
        ultrasonic_thread = threading.Thread(target=ultrasonic_sensor_loop)
        # red_detect_thread = threading.Thread(target=detect_red_loop)

        # Start threads
        ultrasonic_thread.start()
        # red_detect_thread.start()
        print("Threads started.")

        # Join threads to the main thread
        ultrasonic_thread.join()
        print("Ultrasonic thread joined.")
        # red_detect_thread.join()
        # print("Red detection thread joined.")
    except KeyboardInterrupt:
        print("Program stopped by User")
    finally:
        GPIO.cleanup()
        print("GPIO cleanup performed on program exit.")

if __name__ == "__main__":
    main()
