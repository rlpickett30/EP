"""
confidence_manager.py
---------------------

Manages the binning of raw BirdNET confidence scores into compact 3-bit values
for use in low-bandwidth transmission protocols like Avis Lite.

BirdNET returns confidence values as floats between 0.0 and 1.0.
This module compresses those into 8 bins (0–7) based on a nonlinear scale.


Raises ValueError if the confidence is out of range.

Usage:
    from confidence_manager import bin_confidence
    binned = bin_confidence(0.834)
"""

def bin_confidence(raw: float) -> int:
    bins = [
        (0.0000, 0.5001, 0),
        (0.5001, 0.6005, 1),
        (0.6006, 0.7004, 2),
        (0.7005, 0.8000, 3),
        (0.8001, 0.8005, 4),
        (0.8006, 0.9000, 5),
        (0.9001, 0.9005, 6),
        (0.9006, 1.0000, 7),
    ]
    for lo, hi, b in bins:
        if lo <= raw <= hi:
            return b
    raise ValueError(f"[bin_confidence] Invalid confidence: {raw}")
