"""
sht31_driver.py
--------------------

Reads temperature and humidity from the Adafruit SHT31 sensor.

Returns:
    (temperature_C, humidity_percent) as floats

Usage:
    temp, humidity = read_sht31()
"""

import board
import busio
import adafruit_sht31d

def read_sht31():
    """Returns (temperature_C, humidity_percent). Raises on I2C failure."""
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_sht31d.SHT31D(i2c)
    return sensor.temperature, sensor.relative_humidity
