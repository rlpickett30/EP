# node_setup_guide.py

# Connection to network for ssh

hostname -I  # On Pi for ip address

ssh Username@10.1.4.56  # In Terminal or PowerShell



# Setup for a Raspberry Pi 

sudo apt update && sudo apt full-upgrade -y

sudo apt install python3-pip -Y

sudo apt install minicom -y

sudo raspi-config  


sudo apt update && sudo apt full-upgrade -y && sudo apt install python3-pip -Y && sudo apt install minicom -y && sudo raspi-config


    --Choose option 3 Interface Options:
        
        --Choose option I4 SPI
            --Chose yes for Would you like the SPI interface to be enabled?
            
        --Choose option I6 Serial Port
            --Choose no for Would you like a login shell to be accessible over serial?
            --Choose yes for Would you like the serial port hardware to be enabled?
                
        --Finish and select yes for reboot
  
    
  
# Setup guide for BirdNET-Pi installation

pip3 install guizero --break-system-packages && curl -s https://raw.githubusercontent.com/Nachtzuster/BirdNET-Pi/main/newinstaller.sh | bash

    --Your system should reboot
    
    
cd ~
git clone https://github.com/rlpickett30/EP.git
python3 EP/setup_services.py
    

  
# Flashing RAK RUI3 onto Rak3272LP-SIP

Download RAK3272LP-SiP_latest_final.hex from https://downloads.rakwireless.com/#RUI/RUI3/Image/

Using a ST-LINK/V2 in-circuit debugger/programmer and STM32CubeProgrammer software from https://www.st.com/en/development-tools/stm32cubeprog.html flash firmware to RAK3272LP-SiP
  
  

# Setup for Rak3272LP-SIP

--Manual AT Commands



sudo minicom -D /dev/ttyS0 -b 115200 # Manual control for AT Commands

--Make sure you define your own device address and security keys: [WARNING] These must match you node_registry.json
    DEVADDR = "26011B01"
    NWKSKEY = "FADCE1A2D8B50123456789ABCDEF1201"    
    APPSKEY = "1A2B3C4D5E6F7890A1B2C3D4E5F60101"    


sudo pip3 install pyserial --break-system-packages # For running inital_at_setup.py
    

# Using AT Commands

AT Commands take some time to understand so go slow start with. Make sure echo is enabled and enter [AT] in minicom.

You should get [OK] in responce if you have properly setup and wired your Pi

AT Commands for RUI3 are available from https://docs.rakwireless.com/product-categories/software-apis-and-libraries/rui3/at-command-manual/#atmask



# Setup guide for BirdNET-Pi installation

pip3 install guizero --break-system-packages && curl -s https://raw.githubusercontent.com/Nachtzuster/BirdNET-Pi/main/newinstaller.sh | bash

    --Your system should reboot
    --To view the GUI for BirdNET open a web browser and go to    yourhostname.local




sudo apt update && sudo apt full-upgrade -y && sudo apt install python3-pip -y && sudo pip3 install pyserial --break-system-packages && pip3 install guizero --break-system-packages && sudo apt install minicom -y && curl -s https://raw.githubusercontent.com/Nachtzuster/BirdNET-Pi/main/newinstaller.sh | bash

sudo raspi-config


# Navigate to your home directory
cd /home/FLC/EP

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip just in case
pip install --upgrade pip

# Install all required packages
pip install \
    adafruit-blinka \
    adafruit-circuitpython-sht31d \
    adafruit-circuitpython-bmp3xx \
    adafruit-circuitpython-gps \
    RPi.GPIO \
    smbus2 \
    watchdog



















