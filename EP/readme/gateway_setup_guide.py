# gateway_setup_guide.py

# Connection to network for ssh

hostname -I  # On Pi

eg. ssh Node_2@10.1.4.56  # In Terminal or PowerShell

# Setup for a Raspberry Pi 

sudo apt update && sudo apt full-upgrade -y

sudo apt install git -y

sudo raspi-config  

    --Choose option 3 Interface Options:
        
        --Choose option I4 SPI:
            --Choose yes for Would you like the SPI interface to be enabled?
        
        --Choose option I6 Serial Port:
            --Choose no for Would you like a login shell to be accessible over serial?
            --Choose yes for Would you like the serial port hardware to be enabled?  
        
        --Finish and select yes for reboot

# Installation of rak_common_for_gateway for RAK2287 gateway

git clone https://github.com/RAKWireless/rak_common_for_gateway.git

cd rak_common_for_gateway

sudo ./install.sh

    --Choose option 7
    
# Gateway configuration for RAK2287

sudo nano /opt/ttn-gateway/packet_forwarder/lora_pkt_fwd/global_conf.json  # You will need to know your Gateway ID

or

sudo gateway-config

--Take note of the Gateway ID at the top of the window, you will need it for configuration

    --Choose option 4 Edit packet-forwarder config
        --Use global_conf.json to update 
            -- Be sure to update "gateway_ID": "2CCF67FFFE0D5FC0" to your own Gateway ID
            -- Be sure to update "server_address": "10.1.5.18" to your own server ip address
                --ipconfig     # Windows PowerShell 

    --Choose option 3 Restart packet-forwarder
    
# Gateway journal monitoring

cd /opt/ttn-gateway/packet_forwarder/lora_pkt_fwd/

sudo ./lora_pkt_fwd

# Stopping gateway packet forwarder

sudo systemctl stop ttn-gateway




































