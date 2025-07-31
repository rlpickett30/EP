{
  "avis_event": {
    "format": ">B I H B",
    "description": "Bird detection with timestamp, taxonomy code, confidence bin",
    "fields": [
      { "name": "event_type", "type": "uint8", "bytes": 1 },
      { "name": "timestamp", "type": "uint32", "bytes": 4 },
      { "name": "taxonomy", "type": "uint16", "bytes": 2, "map": "taxonomy_map.json" },
      { "name": "confidence", "type": "uint8", "bytes": 1 }
    ],
    "length_bytes": 8
  },
  "weather_event": {
    "format": ">B I b B H",
    "description": "Weather reading with temperature (×2), humidity (%), and pressure (×10)",
    "fields": [
      { "name": "event_type", "type": "uint8", "bytes": 1 },
      { "name": "timestamp", "type": "uint32", "bytes": 4 },
      { "name": "temperature", "type": "int8", "bytes": 1 },
      { "name": "humidity", "type": "uint8", "bytes": 1 },
      { "name": "pressure", "type": "uint16", "bytes": 2 }
    ],
    "length_bytes": 9
  },
  "telemetry_event": {
    "format": ">B I i i h",
    "description": "GPS reading with lat/lon (×1e5), alt (m)",
    "fields": [
      { "name": "event_type", "type": "uint8", "bytes": 1 },
      { "name": "timestamp", "type": "uint32", "bytes": 4 },
      { "name": "lat", "type": "int32", "bytes": 4 },
      { "name": "lon", "type": "int32", "bytes": 4 },
      { "name": "alt", "type": "int16", "bytes": 2 }
    ],
    "length_bytes": 15
  }
}
