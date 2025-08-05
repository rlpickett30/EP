EnviroPulse

EnviroPulse is an off-grid, modular environmental monitoring system designed for bird detection and environmental telemetry using LoRa communication. It runs on Raspberry Pi hardware and RAKwireless LoRa modules, integrating BirdNET-Pi for species identification and local weather data logging.



_____________Key Features_____________

LoRa Node-to-Gateway Communication using RAK3272-SiP and RAK2287

Bird Species Detection via local BirdNET-Pi instance

Weather Sampling (temperature, humidity, pressure)

Binary Payload Protocol for efficient LoRa transmission

Modular Script Architecture with dispatcher-based event routing

Minimalist Logging System for daily JSON archives

Fully Offline Operation with local storage and messaging



_____________Project Structure_____________

EP/
├── logs/                         # Daily JSON logs from the UDP listener
│   └── 07_31_2025.json
│
├── scripts/
│   ├── node/                     # LoRa node logic, drivers, and event samplers
│   │   ├── birdnet_sampler.py
│   │   ├── bmp390_driver.py
│   │   ├── confidence_manager.py
│   │   ├── db_watcher.py
│   │   ├── detection_extractor.py
│   │   ├── dispatcher.py
│   │   ├── gps_calibrator.py
│   │   ├── gps_driver.py
│   │   ├── initial_at_setup.py
│   │   ├── protocol.py
│   │   ├── rui3_driver.py
│   │   ├── send_over_lora.py
│   │   ├── sht31_driver.py
│   │   ├── telemetry_sampler.py
│   │   ├── weather_sampler.py
│   │   ├── confidence_scale_map.json
│   │   ├── event_type_map.json
│   │   ├── structure_protocol.json
│   │   └── taxonomy_map.json
│   │
│   └── server/                   # UDP listener and data ingestion pipeline
│       ├── dispatcher.py
│       ├── lorawan_decryptor.py
│       ├── protocol.py
│       ├── udp_decoder.py
│       ├── udp_listener.py
│       ├── udp_logger.py
│       ├── web_ingestor.py
│       ├── confidence_scale_map.json
│       ├── event_type_map.json
│       ├── node_registry.json
│       ├── structure_protocol.json
│       └── taxonomy_map.json
│
├── setup/
│   ├── conf/                     # Gateway configuration files
│   │   └── global_conf.json
│   │
│   ├── guides/                   # Setup guides for each subsystem
│   │   ├── gateway_setup_guide.py
│   │   ├── node_setup_guide.py
│   │   └── server_setup_guide.py
│   │
│   └── layouts/                  # Visual diagrams and design drawings
│       ├── gateway_script_diagram.drawio
│       ├── node_wiring_diagram.drawio
│       ├── node__script_diagram.drawio
│       ├── presentation.drawio
│       └── server_script_diagram.drawio



_____________Installation_____________

See full instructions in:

setup/guides/node_setup_guide.py

setup/guides/gateway_setup_guide.py

setup/guides/server_setup_guide.py

Each component runs in a separate Python virtual environment.

Example (Node venv install):

cd /home/FLC/EP
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt



_____________Configuration Notes_____________

Be sure to update setup/conf/global_conf.json with your Gateway ID and server IP

Ensure that each node’s DevAddr in initial_at_setup.py matches the entry in node_registry.json

LoRa configuration is handled via AT commands (e.g. AT+MASK, AT+BAND)



_____________Future Goals_____________

Add lightweight local GUI for live data display

Generate automatic daily plots and summary reports

Implement field-deployable enclosures with solar support



_____________License_____________

This project is part of an undergraduate research initiative at Fort Lewis College and is released for educational use. No commercial license is implied.



_____________Acknowledgments_____________

BirdNET-Pi: https://github.com/Nachtzuster/BirdNET-Pi

RAKWireless: https://www.rakwireless.com/

Adafruit CircuitPython Libraries: https://circuitpython.org/