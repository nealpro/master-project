"""
This code is for reference. It is not meant to be executed.
"""

# Imports the required libraries.
import time
import board
import adafruit_tcs34725
# Create a sensor variable to communicate with your sensor. Uses the I2C interface.
i2c = board.I2C()
sensor = adafruit_tcs34725.TCS34725(i2c)
# Set parameters for the sensor
sensor.integration_time = 50
sensor.gain = 4
# Execution loop
while True:
    # Get and print the color detected
    color = sensor.color
    color_rgb = sensor.color_rgb_bytes
    print(
        "RGB color as 8 bitsper chennel int: #{0:02X} or as a 3-tupple: {1}".format(
            color, color_rgb
        )
    )
    # Get and print the temperature intensity
    temp = sensor.color_temperature
    lux = sensor.lux
    print("Temperature: {0}K Lux: {1}\n".format(temp, lux))
    
    # Wait for one second
    time.sleep(1.0)
