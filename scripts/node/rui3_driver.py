"""
rui3_driver.py
--------------

Provides a wrapper for communicating with a RAK RUI3-based LoRa module over UART
using AT command strings.

This driver is used by the send_over_lora module to transmit encoded payloads.

Main class:
- RUI3Driver(port="/dev/ttyS0", baudrate=115200, timeout=5.0)

Methods:
- send_cmd(at_cmd: str) → str: Sends an AT command and reads response
- close()               → void: Closes the serial connection

Usage:
    driver = RUI3Driver()
    resp = driver.send_cmd("AT+SEND=1:112233")
    driver.close()
"""

import serial
import time

class RUI3Driver:
    def __init__(self, port: str = '/dev/ttyS0', baudrate: int = 115200, timeout: float = 5.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=0.5)
        time.sleep(1)
        self._drain_buffers()

    def _drain_buffers(self):
        """Flush input and output buffers."""
        try:
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
        except Exception:
            pass

    def send_cmd(self, at_cmd: str) -> str:
        """
        Send an AT command to the RUI3 module and wait for a response.

        Args:
            at_cmd: Command string, e.g. "AT+SEND=1:112233"

        Returns:
            Multiline string response from the module (joined by '\n')
        """
        cmd = at_cmd.strip() + '\r\n'
        self._drain_buffers()
        self.ser.write(cmd.encode('utf-8'))

        deadline = time.time() + self.timeout
        responses = []
        while time.time() < deadline:
            line = self.ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                responses.append(line)
                if line == 'OK' or 'ERROR' in line:
                    break
        return '\n'.join(responses)

    def close(self):
        """Close the serial connection."""
        try:
            self.ser.close()
        except Exception:
            pass
