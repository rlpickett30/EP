"""
weather_sampler.py
-----------------------

Builds a structured WeatherEvent using SHT31 and BMP390 sensor drivers.

Attributes:
- event_type:   "weather_event"
- temperature:  float (Celsius)
- humidity:     int (percent)
- pressure:     float (hPa)
- time:         int (epoch seconds)
- target:       "send_over_lora"

Usage:
    from node_weather_sampler import WeatherEvent
    event = WeatherEvent.from_sensors()
"""

import time
from sht31_driver import read_sht31  # returns temp/humidity
from bmp390_driver import read_bmp390  # returns pressure

class WeatherEvent:
    def __init__(self, temperature: float, humidity: int, pressure: float, timestamp: int, target: str = "send_over_lora"):
        self.event_type  = "weather_event"
        self.temperature = temperature
        self.humidity    = humidity
        self.pressure    = pressure
        self.time        = timestamp
        self.target      = target

    @classmethod
    def from_sensors(cls):
        """Attempts to read all sensors and return a structured event."""
        try:
            temp, humidity = read_sht31()
            pressure = read_bmp390()
            timestamp = int(time.time())

            return cls(
                temperature=temp,
                humidity=int(humidity),
                pressure=round(pressure, 1),
                timestamp=timestamp
            )
        except Exception as e:
            print(f"[WARN] Weather sensor read failed: {e}")
            return cls(
                temperature=0.0,
                humidity=0,
                pressure=0.0,
                timestamp=int(time.time()),
                target="send_over_lora"
            )

    def __repr__(self):
        return (f"<WeatherEvent {self.temperature:.1f}°C, "
                f"{self.humidity}%RH, {self.pressure:.1f} hPa @ {self.time}>")

    def to_dict(self):
        """Returns the event as a dictionary for LoRa transmission."""
        return {
            "event_type": self.event_type,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "pressure": self.pressure,
            "time": self.time,
            "target": self.target
        }
