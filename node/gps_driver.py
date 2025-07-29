"""
gps_driver.py
------------------
Reads a single GPS fix from the Adafruit Ultimate GPS v3 module over UART.

Returns:
    (latitude, longitude, altitude) as floats

If the fix is not valid, raises RuntimeError.

This driver is called by node_gps_calibrator for repeated sampling.
"""

import time
import serial
import adafruit_gps

# Adjust as needed based on Pi model and configuration
GPS_PORT = "/dev/ttyS0"
GPS_BAUD = 9600

def read_gps_fix(timeout_sec: int = 5):
    """
    Attempts to read a valid GPS fix within the given timeout.
    Returns (lat, lon, alt) as floats, or raises if no fix is found.
    """
    uart = serial.Serial(GPS_PORT, baudrate=GPS_BAUD, timeout=1)
    gps = adafruit_gps.GPS(uart, debug=False)

    # Minimal sentence set + 1Hz update
    gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
    gps.send_command(b"PMTK220,1000")

    start_time = time.time()
    while time.time() - start_time < timeout_sec:
        gps.update()
        if gps.has_fix:
            lat = float(gps.latitude)
            lon = float(gps.longitude)
            alt = float(gps.altitude_m)
            uart.close()
            return lat, lon, alt
        time.sleep(0.5)

    uart.close()
    raise RuntimeError("GPS fix not available within timeout.")

