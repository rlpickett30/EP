"""
gps_calibrator.py
----------------------

Collects GPS readings every 10 seconds for a fixed 15-minute window,
then returns a single averaged lat/lon/alt result.

Intended for stable, low-drift GPS reporting in telemetry events.

Usage:
    from node_gps_calibrator import start_gps_sampling, is_sampling_complete, get_averaged_fix

    start_gps_sampling()       # blocks for 15 minutes
    if is_sampling_complete():
        lat, lon, alt = get_averaged_fix()
"""

import time
from gps_driver import read_gps_fix  # should return (lat, lon, alt)

_SAMPLE_DURATION_SEC = 15 * 60
_SAMPLE_INTERVAL_SEC = 10

_samples = []
_start_time = None
_done = False

def start_gps_sampling():
    """
    Starts a fixed-duration GPS sampling routine (blocking for 15 minutes).
    Collects a new sample every 10 seconds from read_gps_fix().
    Only valid (float) results are stored.
    """
    global _samples, _start_time, _done
    _samples = []
    _start_time = time.time()
    _done = False

    print("Starting 15-minute GPS averaging window...")

    while time.time() - _start_time < _SAMPLE_DURATION_SEC:
        try:
            lat, lon, alt = read_gps_fix()
            if all(isinstance(x, float) for x in (lat, lon, alt)):
                _samples.append((lat, lon, alt))
                print(f"[GPS] Sample {len(_samples)}: {lat:.6f}, {lon:.6f}, {alt:.1f}m")
            else:
                print("[WARN] Invalid GPS sample skipped.")
        except Exception as e:
            print(f"[WARN] GPS read failed: {e}")
        time.sleep(_SAMPLE_INTERVAL_SEC)

    _done = True
    print("GPS averaging complete.")

def is_sampling_complete():
    """Returns True if the sampling window has completed."""
    return _done

def get_averaged_fix():
    """
    Returns (lat, lon, alt) as averaged floats.
    If no valid samples were collected, returns (0.0, 0.0, 0.0).
    Raises if sampling is not yet complete.
    """
    if not _done:
        raise RuntimeError("GPS sampling is not yet complete.")

    if not _samples:
        print("[WARN] No valid GPS samples were collected.")
        return 0.0, 0.0, 0.0

    lat_avg = sum(s[0] for s in _samples) / len(_samples)
    lon_avg = sum(s[1] for s in _samples) / len(_samples)
    alt_avg = sum(s[2] for s in _samples) / len(_samples)
    return lat_avg, lon_avg, alt_avg

def get_sample_count():
    """Returns the number of valid samples collected."""
    return len(_samples)
