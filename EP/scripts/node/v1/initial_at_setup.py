"""
initial_at_setup.py
--------------------

This script performs a one-time setup of the RAK3272 LoRa node using AT commands over UART.
It resets the device to factory defaults, then applies all necessary LoRaWAN ABP configuration
parameters including device address, keys, and channel settings.

Use this script to initialize or reconfigure a node after flashing or hardware changes.
The configuration assumes US915 band (band 5) and ABP activation mode (NJM=0).

Important:
- Requires the rui3_driver.py module in the same directory.
- UART is assumed to be /dev/ttyS0 (adjust if needed).
- Keys should be updated before deployment to match the network’s registry.
"""
import time
from rui3_driver import RUI3Driver

# === YOUR ABP KEYS ===
DEVADDR = "26011B01"
NWKSKEY = "FADCE1A2D8B50123456789ABCDEF1201"
APPSKEY = "1A2B3C4D5E6F7890A1B2C3D4E5F60101"

def run_initial_setup():
    lora = RUI3Driver(port='/dev/ttyS0')
    try:
        print("Resetting and configuring LoRaWAN node...")

        # 1. Full factory reset
        resp = lora.send_cmd("ATZ")
        print("ATZ ->", resp)
        time.sleep(1.5)

        # 2. Reapply all required LoRaWAN config
        cmds = [
            "AT+MODE=0",                 # LoRaWAN mode
            "AT+NJM=0",                  # ABP mode
            "AT+CLASS=A",                # Class A
            "AT+ADR=0",
            "AT+DR=3",
            "AT+BAND=5",                 # US915
            "AT+MASK=0002",              # Adjust to match channel plan
            "AT+CHS=903900000",          # Set default channel freq
            f"AT+DEVADDR={DEVADDR}",
            f"AT+NWKSKEY={NWKSKEY}",
            f"AT+APPSKEY={APPSKEY}"
        ]

        for cmd in cmds:
            resp = lora.send_cmd(cmd)
            print(f"{cmd} -> {resp}")
            time.sleep(.2)


        print("LoRaWAN ABP configuration complete.")

    except Exception as e:
        print("Setup failed:", e)
    finally:
        lora.close()

if __name__ == "__main__":
    run_initial_setup()