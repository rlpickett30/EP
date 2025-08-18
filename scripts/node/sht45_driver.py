"""
sht45_driver.py
--------------------

Reads temperature and humidity from an SHT45 (SHT4x family).

Returns:
    (temperature_C, humidity_percent) as floats

Usage:
    temp, humidity = read_sht45()
"""

import board
import busio
import adafruit_sht4x


def read_sht45(address: int = 0x44, precision: str = "high"):
    """
    Returns (temperature_C, humidity_percent).
    Raises on I2C failure or if sensor is not found.

    precision: "high" (default), "med", or "low"
    """
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_sht4x.SHT4x(i2c, address=address)

    # Set measurement mode (no heater)
    mode_map = {
        "high": adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION,
        "med":  adafruit_sht4x.Mode.NOHEAT_MEDPRECISION,
        "low":  adafruit_sht4x.Mode.NOHEAT_LPRECISION,
    }
    sensor.mode = mode_map.get(precision, mode_map["high"])

    temperature, relative_humidity = sensor.measurements  # triggers a read
    return float(temperature), float(relative_humidity)
