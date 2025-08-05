"""
setup_services.py
-----------------

Automates the installation of systemd services for EnviroPulse.

- Copies dispatcher.service and initial_at_setup.service to /etc/systemd/system/
- Reloads systemd daemon
- Enables both services to run at boot
- Optionally starts both services immediately

Usage:
    sudo python3 setup_services.py
"""

import subprocess
from pathlib import Path
import sys

# Paths to your service files in the repo
SERVICE_DIR = Path(__file__).parent / "services"
SERVICES = ["initial_at_setup.service", "dispatcher.service"]

def run(cmd):
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

def install_service(service_name):
    source = SERVICE_DIR / service_name
    destination = Path("/etc/systemd/system") / service_name

    if not source.exists():
        print(f"[ERROR] Service file not found: {source}")
        sys.exit(1)

    print(f"[INFO] Installing {service_name}...")
    run(["sudo", "cp", str(source), str(destination)])

def main():
    print("== EnviroPulse Service Installer ==")

    for service in SERVICES:
        install_service(service)

    print("[INFO] Reloading systemd daemon...")
    run(["sudo", "systemctl", "daemon-reexec"])
    run(["sudo", "systemctl", "daemon-reload"])

    for service in SERVICES:
        print(f"[INFO] Enabling {service} to start on boot...")
        run(["sudo", "systemctl", "enable", service])

        print(f"[INFO] Starting {service} now...")
        run(["sudo", "systemctl", "start", service])

    print("== All services installed and started successfully. ==")

if __name__ == "__main__":
    if not Path("/etc/systemd/system").exists():
        print("[ERROR] This script must be run on a Linux system with systemd.")
        sys.exit(1)

    if not (Path("/usr/bin/sudo").exists() or Path("/bin/sudo").exists()):
        print("[ERROR] This script requires sudo privileges.")
        sys.exit(1)

    main()
