EnviroPulse

EnviroPulse is an off-grid, modular environmental monitoring system designed for bird detection and environmental telemetry using LoRa communication. It runs on Raspberry Pi hardware and RAKwireless LoRa modules, integrating BirdNET-Pi for species identification and local weather data logging.



***Key Features***

LoRa Node-to-Gateway Communication using RAK3272-SiP and RAK2287

Bird Species Detection via local BirdNET-Pi instance

Weather Sampling (temperature, humidity, pressure)

Binary Payload Protocol for efficient LoRa transmission

Modular Script Architecture with dispatcher-based event routing

Minimalist Logging System for daily JSON archives

Fully Offline Operation with local storage and messaging



***Project Structure***

EP/
├── logs/                         # Daily JSON logs from the UDP listener
│   └── 07\_31\_2025.json
│
├── scripts/
│   ├── node/                     # LoRa node logic, drivers, and event samplers
│   │   ├── birdnet\_sampler.py
│   │   ├── bmp390\_driver.py
│   │   ├── confidence\_manager.py
│   │   ├── db\_watcher.py
│   │   ├── detection\_extractor.py
│   │   ├── dispatcher.py
│   │   ├── gps\_calibrator.py
│   │   ├── gps\_driver.py
│   │   ├── initial\_at\_setup.py
│   │   ├── protocol.py
│   │   ├── rui3\_driver.py
│   │   ├── send\_over\_lora.py
│   │   ├── sht31\_driver.py
│   │   ├── telemetry\_sampler.py
│   │   ├── weather\_sampler.py
│   │   ├── confidence\_scale\_map.json
│   │   ├── event\_type\_map.json
│   │   ├── structure\_protocol.json
│   │   └── taxonomy\_map.json
│   │
│   └── server/                   # UDP listener and data ingestion pipeline
│       ├── dispatcher.py
│       ├── lorawan\_decryptor.py
│       ├── protocol.py
│       ├── udp\_decoder.py
│       ├── udp\_listener.py
│       ├── udp\_logger.py
│       ├── web\_ingestor.py
│       ├── confidence\_scale\_map.json
│       ├── event\_type\_map.json
│       ├── node\_registry.json
│       ├── structure\_protocol.json
│       └── taxonomy\_map.json
│
├── setup/
│   ├── conf/                     # Gateway configuration files
│   │   └── global\_conf.json
│   │
│   ├── guides/                   # Setup guides for each subsystem
│   │   ├── gateway\_setup\_guide.py
│   │   ├── node\_setup\_guide.py
│   │   └── server\_setup\_guide.py
│   │
│   └── layouts/                  # Visual diagrams and design drawings
│       ├── gateway\_script\_diagram.drawio
│       ├── node\_wiring\_diagram.drawio
│       ├── node\_\_script\_diagram.drawio
│       ├── presentation.drawio
│       └── server\_script\_diagram.drawio



***Installation***

See full instructions in:

setup/guides/node\_setup\_guide.py

setup/guides/gateway\_setup\_guide.py

setup/guides/server\_setup\_guide.py

Each component runs in a separate Python virtual environment.

Example (Node venv install):

cd /home/FLC/EP
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt



***Configuration Notes***

Be sure to update setup/conf/global\_conf.json with your Gateway ID and server IP

Ensure that each node’s DevAddr in initial\_at\_setup.py matches the entry in node\_registry.json

LoRa configuration is handled via AT commands (e.g. AT+MASK, AT+BAND)



***Future Goals***

Add lightweight local GUI for live data display

Generate automatic daily plots and summary reports

Implement field-deployable enclosures with solar support



***License***

This project is part of an undergraduate research initiative at Fort Lewis College and is released for educational use only. No commercial license is implied.



***Acknowledgments***

BirdNET-Pi: https://github.com/Nachtzuster/BirdNET-Pi

RAKWireless: https://www.rakwireless.com/

Adafruit CircuitPython Libraries: https://circuitpython.org/

