import time
import board
import adafruit_tcs34725
import digitalio
import pigpio

pi = pigpio.pi()
if not pi.connected:
    exit()

# Corrected pin configuration according to board library's naming
ULTRASONIC_1_TRIG = board.D17
ULTRASONIC_1_ECHO = board.D27
ULTRASONIC_2_TRIG = board.D16
ULTRASONIC_2_ECHO = board.D20
RELAY_1 = board.D19
RELAY_2 = board.D26
BUZZER = 12  # GPIO 12 for PWM, assuming you are using a pin that supports hardware PWM

# RGB sensor setup
i2c = board.I2C()
sensor = adafruit_tcs34725.TCS34725(i2c)
sensor.integration_time = 50
sensor.gain = 4

print("RGB sensor initialized")

# GPIO setup
ultrasonic_1_trig = digitalio.DigitalInOut(ULTRASONIC_1_TRIG)
ultrasonic_1_trig.direction = digitalio.Direction.OUTPUT

ultrasonic_1_echo = digitalio.DigitalInOut(ULTRASONIC_1_ECHO)
ultrasonic_1_echo.direction = digitalio.Direction.INPUT

print("Ultrasonic sensor 1 initialized")

ultrasonic_2_trig = digitalio.DigitalInOut(ULTRASONIC_2_TRIG)
ultrasonic_2_trig.direction = digitalio.Direction.OUTPUT

ultrasonic_2_echo = digitalio.DigitalInOut(ULTRASONIC_2_ECHO)
ultrasonic_2_echo.direction = digitalio.Direction.INPUT

print("Ultrasonic sensor 2 initialized")

relay_1 = digitalio.DigitalInOut(RELAY_1)
relay_1.direction = digitalio.Direction.OUTPUT

relay_2 = digitalio.DigitalInOut(RELAY_2)
relay_2.direction = digitalio.Direction.OUTPUT

print("Relays initialized")

# PWM setup for buzzer using pigpio
pi.set_mode(BUZZER, pigpio.OUTPUT)
# Set the buzzer frequency to 440Hz with a duty cycle of 50%
pi.hardware_PWM(BUZZER, 440, 500000)  

print("Buzzer initialized")

def distance(trig, echo):
    trig.value = True
    time.sleep(0.00001)  # 10us delay
    trig.value = False

    start_time = time.time()
    while echo.value == False:
        if time.time() - start_time > 0.01:  # timeout after 10ms
            return None
        pass

    while echo.value == True:
        stop_time = time.time()
        if time.time() - start_time > 0.01:  # timeout after 10ms
            return None
        pass

    time_elapsed = stop_time - start_time
    distance_cm = (time_elapsed * 34300) / 2
    return distance_cm

def main():
    try:
        while True:
            dist1 = distance(ultrasonic_1_trig, ultrasonic_1_echo)
            dist2 = distance(ultrasonic_2_trig, ultrasonic_2_echo)

            if dist1 is not None:
                print("Distance 1: {:.2f} cm".format(dist1))
                if dist1 < 200:
                    print("Distance 1: In range")
                    relay_1.value = True
                else:
                    print("Distance 1: Out of range")
                    relay_1.value = False
            else:
                print("Distance 1: Measurement timed out")

            if dist2 is not None:
                print("Distance 2: {:.2f} cm".format(dist2))
                if dist2 < 700:
                    print("Distance 2: In range")
                    pi.hardware_PWM(BUZZER, 440, 500000)  # Turn on buzzer
                else:
                    print("Distance 2: Out of range")
                    pi.hardware_PWM(BUZZER, 0, 0)  # Turn off buzzer
            else:
                print("Distance 2: Measurement timed out")

            color_rgb = sensor.color_rgb_bytes
            print("Detected color (RGB):", color_rgb)
            if color_rgb[0] > 100 and color_rgb[1] < 50 and color_rgb[2] < 50:
                print("Red detected")
                relay_2.value = True
            else:
                relay_2.value = False
                print("No red detected")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Program stopped by User")
    finally:
        pi.stop()

if __name__ == "__main__":
    main()
