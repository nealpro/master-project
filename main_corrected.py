import RPi.GPIO as GPIO
import time
import board
import adafruit_tcs34725

# Ensure GPIO warnings are displayed
GPIO.setwarnings(True)

# Pins configuration
ULTRASONIC_1_TRIG = 17
ULTRASONIC_1_ECHO = 27
ULTRASONIC_2_TRIG = 23
ULTRASONIC_2_ECHO = 24
RELAY_1 = 21
RELAY_2 = 26
BUZZER = 7
BUTTON = 18

# Constants
DEBOUNCE_TIME = 2  # seconds
DISTANCE_THRESHOLD_1 = 200  # cm
DISTANCE_THRESHOLD_2 = 700  # cm
RELAY_TOGGLE_DELAY = 2  # seconds

# State variables
relay1_state = False
relay2_state = False
relay1_last_toggle_time = time.time()
relay2_last_toggle_time = time.time()

# Set GPIO mode
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
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# PWM setup for buzzer
Buzz = GPIO.PWM(BUZZER, 440)  # 440Hz frequency

def distance(trig, echo):
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
    return (time_elapsed * 34300) / 2

def toggle_relay(relay_pin, state):
    GPIO.output(relay_pin, state)

def main():
    try:
        button_pressed = False
        Buzz.start(50)  # Prepare buzzer but don't emit sound yet
        Buzz.ChangeDutyCycle(0)

        while True:
            button_pressed = not GPIO.input(BUTTON)  # Button is active-low

            # Measure distances
            dist1 = distance(ULTRASONIC_1_TRIG, ULTRASONIC_1_ECHO)
            dist2 = distance(ULTRASONIC_2_TRIG, ULTRASONIC_2_ECHO)

            # Relay 1 control
            if dist1 < DISTANCE_THRESHOLD_1 and not relay1_state and (time.time() - relay1_last_toggle_time) > DEBOUNCE_TIME:
                relay1_state = True
                relay1_last_toggle_time = time.time()
                toggle_relay(RELAY_1, GPIO.HIGH)
            elif dist1 >= DISTANCE_THRESHOLD_1 and relay1_state:
                relay1_state = False
                toggle_relay(RELAY_1, GPIO.LOW)

            # Relay 2 and buzzer control
            if dist2 < DISTANCE_THRESHOLD_2 and not relay2_state and (time.time() - relay2_last_toggle_time) > DEBOUNCE_TIME:
                relay2_state = True
                relay2_last_toggle_time = time.time()
                toggle_relay(RELAY_2, GPIO.HIGH)
                Buzz.ChangeDutyCycle(50)  # Emit sound
            elif dist2 >= DISTANCE_THRESHOLD_2 and relay2_state:
                relay2_state = False
                toggle_relay(RELAY_2, GPIO.LOW)
                Buzz.ChangeDutyCycle(0)  # Stop sound

            # Check for red color detection
            color_rgb = sensor.color_rgb_bytes
            # Check if the dominant color is red, and if so, toggle the relay
            if color_rgb[0] > 100 and color_rgb[1] < 50 and color_rgb[2] < 50:
                # Only toggle the relay if enough time has passed since the last toggle
                if time.time() - relay1_last_toggle_time > RELAY_TOGGLE_DELAY:
                    relay1_state = not relay1_state  # Toggle the state
                    relay1_last_toggle_time = time.time()  # Update the last toggle time
                    toggle_relay(RELAY_1, GPIO.HIGH if relay1_state else GPIO.LOW)
                    print(f"Vibration motor {'on' if relay1_state else 'off'}.")
                                    # If red is detected and relay is not already on, turn it on
                if not relay1_state:
                    relay1_state = True
                    relay1_last_toggle_time = time.time()
                    toggle_relay(RELAY_1, GPIO.HIGH)
            else:
                # If red is not detected and relay is on, turn it off
                if relay1_state:
                    relay1_state = False
                    toggle_relay(RELAY_1, GPIO.LOW)

            # Check if button has been pressed to exit the loop
            if button_pressed:
                print("Button pressed, exiting loop.")
                break

            time.sleep(0.1)  # Short delay to avoid excessive CPU usage

    except KeyboardInterrupt:
        print("Program stopped by User")
    finally:
        Buzz.stop()
        GPIO.cleanup()
        print("GPIO cleanup performed on program exit.")

if __name__ == "__main__":
    main()
