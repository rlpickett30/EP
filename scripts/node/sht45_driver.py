"""
sht45_driver.py
--------------------
Reads temperature (°C) and humidity (%) from an SHT45/SHT4x.

Usage:
    temp_c, rh = read_sht45()
"""

import board
import busio
import adafruit_sht4x


def read_sht45(address: int = 0x44):
    """Return (temperature_C, humidity_percent). Raises on I2C failure."""
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_sht4x.SHT4x(i2c, address=address)
    t_c, rh = sensor.measurements  # triggers a read
    return float(t_c), float(rh)