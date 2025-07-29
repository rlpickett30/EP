"""
rui3_driver.py
---------------

This module provides a lightweight serial interface to RAKwireless LoRa modules 
running RUI3 firmware using AT commands over UART.

It defines the RUI3Driver class, which is responsible for:
- Opening and managing a serial connection to the LoRa module
- Sending AT commands and reading responses
- Handling basic timing, flushing, and cleanup

Key features:
- Automatically clears serial buffers on each call
- Waits for a response up to a user-defined timeout
- Captures multi-line replies until 'OK' or 'ERROR' is detected

Usage:
  from rui3_driver import RUI3Driver
  lora = RUI3Driver(port='/dev/ttyS0')
  response = lora.send_cmd("AT+SEND=1:hello")
  lora.close()

Default serial port: /dev/ttyS0  
Baud rate: 115200  
Timeout: 5 seconds

This module is designed to be shared across all scripts interacting with a RUI3 LoRa node.
"""

import serial
import time

class RUI3Driver:
    """
    RUI3Driver wraps a RAK RUI3-based LoRa module over serial AT commands.

    Methods:
    - send_cmd(at_cmd: str) -> str: send an AT command (without CRLF) and wait for response
    - close(): close the serial port
    """
    def __init__(self, port: str = '/dev/ttyS0', baudrate: int = 115200, timeout: float = 5.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        # Open serial port
        self.ser = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=0.5)
        # Give the module a moment to initialize
        time.sleep(1)
        # Clear any existing data
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
        Send an AT command to the RUI3 module and wait for an OK or ERROR response.

        Args:
            at_cmd: the command string, e.g. "AT+SEND=1:112233"

        Returns:
            The raw response from the module (multiple lines joined by '\n').
        """
        cmd = at_cmd.strip() + '\r\n'
        self._drain_buffers()
        # Write the command
        self.ser.write(cmd.encode('utf-8'))

        # Read lines until OK or ERROR, or until timeout
        deadline = time.time() + self.timeout
        responses = []
        while time.time() < deadline:
            line = self.ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                responses.append(line)
                # break on definitive response
                if line == 'OK' or 'ERROR' in line:
                    break
        return '\n'.join(responses)

    def close(self):
        """Close the serial connection."""
        try:
            self.ser.close()
        except Exception:
            pass