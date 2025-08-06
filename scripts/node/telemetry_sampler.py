"""
telemetry_sampler.py
--------------------------
Takes a single GPS fix and creates a structured TelemetryEvent.

Attributes:
- event_type: "telemetry_event"
- lat:        float (decimal degrees)
- lon:        float (decimal degrees)
- alt:        float (meters)
- time:       int (epoch seconds)
- target:     "send_over_lora"

Usage:
    from telemetry_sampler import TelemetryEvent
    event = TelemetryEvent.from_gps()
"""

import time
from gps_driver import read_gps_fix
from debug_logger import log_debug, log_error

class TelemetryEvent:
    def __init__(self, lat: float, lon: float, alt: float, timestamp: int, target: str = "send_over_lora"):
        self.event_type = "telemetry_event"
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.time = timestamp
        self.target = target

    @classmethod
    def from_gps(cls):
        """Takes a single GPS reading (non-blocking)."""
        try:
            lat, lon, alt = read_gps_fix(timeout_sec=60)
            if not all(isinstance(x, float) for x in (lat, lon, alt)):
                raise ValueError("Invalid GPS fix type")
            log_debug(f"GPS fix acquired: lat={lat:.6f}, lon={lon:.6f}, alt={alt:.1f}")
        except Exception as e:
            log_error(f"Failed to read GPS fix: {e}")
            lat, lon, alt = 0.0, 0.0, 0.0

        timestamp = int(time.time())
        return cls(lat=lat, lon=lon, alt=alt, timestamp=timestamp)

    def __repr__(self):
        return (f"<TelemetryEvent lat={self.lat:.6f}, lon={self.lon:.6f}, "
                f"alt={self.alt:.1f}m @ {self.time}>")

    def to_dict(self):
        return {
            "event_type": self.event_type,
            "lat": int(self.lat * 1e5),
            "lon": int(self.lon * 1e5),
            "alt": int(self.alt),
            "timestamp": self.time,
            "target": self.target
        }