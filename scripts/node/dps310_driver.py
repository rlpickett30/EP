"""
dps310_driver.py
---------------------

Reads barometric pressure from the Adafruit DPS310 sensor.

Returns:
    pressure in hPa (hectopascals)

Usage:
    pressure = read_dps310()
"""

import board
import busio
import adafruit_dps310


def read_dps310(address: int = 0x77):
    """Returns barometric pressure in hPa. Raises on I2C failure."""
    i2c = busio.I2C(board.SCL, board.SDA)
    dps = adafruit_dps310.DPS310(i2c, address=address)
    return float(dps.pressure)
