import time
import threading
import board
import adafruit_tcs34725
import digitalio
import pulseio

# Pins configuration
ULTRASONIC_1_TRIG = board.D17
ULTRASONIC_1_ECHO = board.D27
ULTRASONIC_2_TRIG = board.D16
ULTRASONIC_2_ECHO = board.D20
RELAY_1 = board.D19
RELAY_2 = board.D26
BUZZER = board.D21

# RGB sensor setup
i2c = board.I2C()
sensor = adafruit_tcs34725.TCS34725(i2c)
sensor.integration_time = 50
sensor.gain = 4

# GPIO setup
ultrasonic_1_trig = digitalio.DigitalInOut(ULTRASONIC_1_TRIG)
ultrasonic_1_trig.direction = digitalio.Direction.OUTPUT

ultrasonic_1_echo = digitalio.DigitalInOut(ULTRASONIC_1_ECHO)
ultrasonic_1_echo.direction = digitalio.Direction.INPUT

ultrasonic_2_trig = digitalio.DigitalInOut(ULTRASONIC_2_TRIG)
ultrasonic_2_trig.direction = digitalio.Direction.OUTPUT

ultrasonic_2_echo = digitalio.DigitalInOut(ULTRASONIC_2_ECHO)
ultrasonic_2_echo.direction = digitalio.Direction.INPUT

relay_1 = digitalio.DigitalInOut(RELAY_1)
relay_1.direction = digitalio.Direction.OUTPUT

relay_2 = digitalio.DigitalInOut(RELAY_2)
relay_2.direction = digitalio.Direction.OUTPUT

# PWM setup for buzzer
buzzer = pulseio.PWMOut(BUZZER, duty_cycle=0, frequency=440)

def distance(trig, echo):
    trig.value = True
    time.sleep(0.00001)  # 10us delay
    trig.value = False

    start_time = time.monotonic()
    while echo.value == False:
        start_time = time.monotonic()

    stop_time = time.monotonic()
    while echo.value == True:
        stop_time = time.monotonic()

    time_elapsed = stop_time - start_time
    distance = (time_elapsed * 34300) / 2

    return distance

def ultrasonic_sensor_loop():
    while True:
        dist1 = distance(ultrasonic_1_trig, ultrasonic_1_echo)
        dist2 = distance(ultrasonic_2_trig, ultrasonic_2_echo)

        if dist1 < 200:
            relay_1.value = True
        else:
            relay_1.value = False

        if dist2 < 700:
            buzzer.duty_cycle = 32767  # 50% duty cycle
        else:
            buzzer.duty_cycle = 0

        time.sleep(0.1)

def detect_red_loop():
    while True:
        color_rgb = sensor.color_rgb_bytes
        if color_rgb[0] > 100 and color_rgb[1] < 50 and color_rgb[2] < 50:
            print("Red detected")
            relay_2.value = True
        else:
            relay_2.value = False

        time.sleep(0.1)

def main():
    try:
        ultrasonic_thread = threading.Thread(target=ultrasonic_sensor_loop)
        red_detect_thread = threading.Thread(target=detect_red_loop)

        ultrasonic_thread.start()
        red_detect_thread.start()

        ultrasonic_thread.join()
        red_detect_thread.join()
    except KeyboardInterrupt:
        print("Program stopped by User")

if __name__ == "__main__":
    main()
