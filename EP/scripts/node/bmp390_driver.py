"""
bmp390_driver.py
---------------------

Reads barometric pressure from the Adafruit BMP390 sensor.

Returns:
    pressure in hPa (hectopascals)

Usage:
    pressure = read_bmp390()
"""

import board
import busio
import adafruit_bmp3xx

def read_bmp390():
    """Returns barometric pressure in hPa. Raises on I2C failure."""
    i2c = busio.I2C(board.SCL, board.SDA)
    bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c)
    return bmp.pressure
