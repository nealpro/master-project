import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)
GPIO.setup(37, GPIO.OUT)
GPIO.output(37, GPIO.HIGH)
time.sleep(10)
GPIO.output(37, GPIO.LOW)