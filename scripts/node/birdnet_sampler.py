"""
birdnet_sampler.py
------------------

Builds a structured BirdDetectionEvent from a raw SQLite row.

If input data is missing or malformed, constructs a fallback
event with event_type = "birdnet_error".

Attributes:
- event_type:     (str) e.g. "avis_event", "birdnet_error"
- common_name:    (str) species name or "unknown"
- timestamp:      (int) epoch seconds
- confidence_bin: (int) 0–7 for valid, 0 if fallback
- target:         (str) routing label or "send_over_lora"
"""

import time
from confidence_manager import bin_confidence

class BirdDetectionEvent:
    def __init__(self, event_type: str, common_name: str, timestamp: int, confidence_bin: int, target: str = "send_over_lora"):
        self.event_type     = event_type
        self.common_name    = common_name
        self.time           = timestamp
        self.confidence_bin = confidence_bin
        self.target         = target

    @classmethod
    def from_row(cls, row: dict, event_type: str = "avis_event", target: str = "send_over_lora"):
        """
        Constructs a BirdDetectionEvent from a raw detection row.
        Falls back to 'birdnet_error' if malformed or missing data.
        """
        try:
            ts_str = f"{row['Date']}T{row['Time']}Z"
            timestamp = int(time.mktime(time.strptime(ts_str, "%Y-%m-%dT%H:%M:%SZ")))

            common_name = row["Com_Name"]
            confidence = float(row["Confidence"])
            conf_bin = bin_confidence(confidence)

            return cls(
                event_type=event_type,
                common_name=common_name,
                timestamp=timestamp,
                confidence_bin=conf_bin,
                target=target
            )

        except (KeyError, ValueError, TypeError) as e:
            print(f"[WARN] Bad BirdNET row: {e}")
            return cls(
                event_type="birdnet_error",
                common_name="unknown",
                timestamp=int(time.time()),
                confidence_bin=0,
                target=target
            )

    def to_dict(self):
        """
        Converts this event to a dictionary suitable for Protocol.encode().
        """
        return {
            "event_type": self.event_type,
            "timestamp": self.time,
            "common_name": self.common_name,
            "confidence": self.confidence_bin,
            "target": self.target
        }

    def __repr__(self):
        return (f"<BirdDetectionEvent '{self.common_name}' "
                f"(conf_bin={self.confidence_bin}) @ {self.time}>")