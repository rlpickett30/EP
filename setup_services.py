"""
setup_services.py
-----------------

Automates EnviroPulse setup:
- Creates Python virtual environment
- Installs requirements.txt
- Patches service files with correct Python path
- Installs and enables dispatcher + setup services

Usage:
    sudo python3 setup_services.py
"""

import subprocess
from pathlib import Path
import sys
import shutil

SERVICE_DIR = Path(__file__).parent / "services"
SCRIPTS_DIR = Path(__file__).parent / "scripts" / "node"
VENV_DIR = Path(__file__).parent / "venv"
REQUIREMENTS_FILE = Path(__file__).parent / "requirements.txt"

SERVICES = {
    "initial_at_setup.service": {
        "target_script": SCRIPTS_DIR / "initial_at_setup.py"
    },
    "dispatcher.service": {
        "target_script": SCRIPTS_DIR / "dispatcher.py"
    }
}

def run(cmd):
    print(f"Running: {' '.join(str(c) for c in cmd)}")
    subprocess.run(cmd, check=True)

def create_virtualenv():
    if not VENV_DIR.exists():
        print("[INFO] Creating virtual environment...")
        run(["python3", "-m", "venv", str(VENV_DIR)])
    else:
        print("[INFO] Virtual environment already exists.")

def install_requirements():
    if REQUIREMENTS_FILE.exists():
        print("[INFO] Installing dependencies from requirements.txt...")
        run([str(VENV_DIR / "bin" / "pip"), "install", "-r", str(REQUIREMENTS_FILE)])
    else:
        print("[WARNING] requirements.txt not found. Skipping dependency install.")

def patch_and_install_service(service_name, python_path):
    source = SERVICE_DIR / service_name
    target = Path("/etc/systemd/system") / service_name

    if not source.exists():
        print(f"[ERROR] Missing service file: {source}")
        sys.exit(1)

    with open(source, "r") as f:
        contents = f.read()

    # Replace ExecStart with interpreter + script path
    target_script = SERVICES[service_name]["target_script"]
    exec_line = f"ExecStart={python_path} {target_script}"

    patched_contents = []
    for line in contents.splitlines():
        if line.startswith("ExecStart="):
            patched_contents.append(exec_line)
        else:
            patched_contents.append(line)

    temp_path = SERVICE_DIR / f"patched_{service_name}"
    with open(temp_path, "w") as f:
        f.write("\n".join(patched_contents))

    print(f"[INFO] Installing {service_name}...")
    run(["sudo", "cp", str(temp_path), str(target)])
    temp_path.unlink()

def main():
    print("== EnviroPulse Full Setup ==")

    create_virtualenv()
    install_requirements()

    python_path = str(VENV_DIR / "bin" / "python")

    for service in SERVICES:
        patch_and_install_service(service, python_path)

    print("[INFO] Reloading systemd...")
    run(["sudo", "systemctl", "daemon-reexec"])
    run(["sudo", "systemctl", "daemon-reload"])

    for service in SERVICES:
        run(["sudo", "systemctl", "enable", service])
        run(["sudo", "systemctl", "restart", service])

    print("== Setup complete. Services installed and running. ==")

if __name__ == "__main__":
    if not Path("/etc/systemd/system").exists():
        print("[ERROR] This script must be run on a Linux system with systemd.")
        sys.exit(1)
    main()
