"""
telemetry_sampler.py
--------------------------
Runs a 15-minute GPS sampling session and creates a structured
TelemetryEvent for transmission.

Attributes:
- event_type: "telemetry_event"
- lat:        float (decimal degrees)
- lon:        float (decimal degrees)
- alt:        float (meters)
- time:       int (epoch seconds)
- target:     "send_over_lora"

Usage:
    from node_telemetry_sampler import TelemetryEvent
    TelemetryEvent.start_gps_session()
    event = TelemetryEvent.from_calibrator()
"""

import time
from gps_calibrator import (
    start_gps_sampling,
    is_sampling_complete,
    get_averaged_fix
)

class TelemetryEvent:
    def __init__(self, lat: float, lon: float, alt: float, timestamp: int, target: str = "send_over_lora"):
        self.event_type = "telemetry_event"
        self.lat        = lat
        self.lon        = lon
        self.alt        = alt
        self.time       = timestamp
        self.target     = target

    @classmethod
    def from_calibrator(cls):
        """
        Reads from the completed GPS calibrator session and returns a telemetry event.
        Falls back to (0.0, 0.0, 0.0) if no samples were available.
        """
        if not is_sampling_complete():
            raise RuntimeError("GPS sampling is not yet complete.")

        lat, lon, alt = get_averaged_fix()
        timestamp = int(time.time())

        return cls(lat=lat, lon=lon, alt=alt, timestamp=timestamp)

    @staticmethod
    def start_gps_session():
        """Launches 15-minute GPS sample collection (blocking)."""
        start_gps_sampling()

    def __repr__(self):
        return (f"<TelemetryEvent lat={self.lat:.6f}, lon={self.lon:.6f}, "
                f"alt={self.alt:.1f}m @ {self.time}>")

    def to_dict(self):
        """Returns the event as a dictionary for LoRa transmission."""
        return {
            "event_type": self.event_type,
            "lat": self.lat,
            "lon": self.lon,
            "alt": self.alt,
            "time": self.time,
            "target": self.target
        }
