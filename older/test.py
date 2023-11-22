import RPi.GPIO as GPIO
import time
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
GPIO.setup(35, GPIO.OUT)
GPIO.output(35, GPIO.HIGH)
time.sleep(10)
GPIO.output(35, GPIO.LOW)