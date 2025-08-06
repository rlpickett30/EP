# debug_logger.py

from datetime import datetime

def log_debug(msg: str):
    print(f"[DEBUG] {datetime.now().isoformat()} - {msg}")

def log_error(msg: str):
    print(f"[ERROR] {datetime.now().isoformat()} - {msg}")
