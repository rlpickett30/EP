"""
weather_sampler.py
-----------------------

Builds a structured WeatherEvent using SHT31 and BMP390 sensor drivers.

Attributes:
- event_type:   "weather_event"
- temperature:  int (°C ×2, signed 8-bit)
- humidity:     int (percent, uint8)
- pressure:     int (hPa ×10, uint16)
- timestamp:    int (epoch seconds)
- target:       "send_over_lora"

Usage:
    from weather_sampler import WeatherEvent
    event = WeatherEvent.from_sensors()
"""

import time
from sht45_driver import read_sht45  # returns (temp: float, humidity: float)
from dps310_driver import read_dps310  # returns pressure: float

class WeatherEvent:
    def __init__(self, temperature: int, humidity: int, pressure: int, timestamp: int, target: str = "send_over_lora"):
        self.event_type  = "weather_event"
        self.temperature = temperature    # °C ×2 → int8
        self.humidity    = humidity       # % → uint8
        self.pressure    = pressure       # hPa ×10 → uint16
        self.timestamp   = timestamp      # epoch seconds
        self.target      = target

    @classmethod
    def from_sensors(cls):
        """Attempts to read all sensors and return a structured event."""
        try:
            temp, humidity = read_sht45()
            pressure = read_dps310()
            timestamp = int(time.time())

            return cls(
                temperature=int(round(temp)),         # scale °C
                humidity=int(round(humidity)),            # whole percent
                pressure=int(round(pressure * 10)),       # scale hPa
                timestamp=timestamp
            )
        except Exception as e:
            print(f"[WARN] Weather sensor read failed: {e}")
            return cls(
                temperature=0,
                humidity=0,
                pressure=0,
                timestamp=int(time.time()),
                target="send_over_lora"
            )

    def __repr__(self):
        return (f"<WeatherEvent {self.temperature / 2:.1f}°C, "
                f"{self.humidity}%RH, {self.pressure / 10:.1f} hPa @ {self.timestamp}>")

    def to_dict(self):
        """Returns the event as a dictionary for LoRa transmission."""
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "pressure": self.pressure,
            "target": self.target
        }
