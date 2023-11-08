import pigpio
import time

# Initialize pigpio
pi = pigpio.pi()

# Define your buzzer pin
BUZZER = 17 # Use the BCM pin number

# Set the buzzer pin as an output
pi.set_mode(BUZZER, pigpio.OUTPUT)

# Start PWM on the buzzer pin at 440Hz with 50% duty cycle
pi.hardware_PWM(BUZZER, 440, 500000)

time.sleep(1)  # Keep the buzzer on for 1 second

# Stop PWM on the buzzer pin
pi.set_PWM_dutycycle(BUZZER, 0)

# Cleanup and disconnect from pigpio daemon
pi.stop()
