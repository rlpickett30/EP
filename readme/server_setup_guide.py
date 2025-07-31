# server_setup_guide.py

# Needed scripts

lorawan_crypto.py
decrypt_uplink.py
extract_and_decrypt.py
udp_listener.py
node_registry.json

# Node registry configuration

[WARNING] Key configuration must match the node key configuration. 

Edit node_registry.json to match your node configuration

# Launching the listener for your server

python udp_listener.py     # In PowerShell

Port 1700 is now open and should be pushing acknowledgments to your gateway


