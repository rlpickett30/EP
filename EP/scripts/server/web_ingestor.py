"""
web_ingestor.py
---------------

Handles ingesting decoded Avis events into the Node.js web backend.

Responsibilities:
- Look up the most recent session ID from users.db
- Build a JSON payload from the event
- POST it to /api/ingest on the local server

Requirements:
- The Node.js server must be reachable via LAN/IP
- This module only handles Bird (type 1) events

Usage:
    from web_ingestor import ingest_avis_event
    ingest_avis_event(event_dict)
"""

import sqlite3
import requests

DB_PATH = "/home/ewan/Desktop/projects/web/users.db"
INGEST_URL = "http://192.168.1.50:3000/api/ingest"


def get_active_session_id():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
          SELECT session_id
            FROM sessions
           ORDER BY p_date DESC
           LIMIT 1
        """)
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print(f"[web_ingestor] Failed to fetch session_id: {e}")
        return None


def ingest_avis_event(event: dict):
    session_id = get_active_session_id()
    if session_id is None:
        print("[web_ingestor] No active session — skipping ingest")
        return

    payload = {
        "type": 1,
        "session_id": session_id,
        "node_id": event.get("devaddr"),
        "common_name": event.get("common_name"),
        "confidence_level": event.get("confidence_bin"),
        "time_stamp": event.get("event_timestamp")
    }

    try:
        resp = requests.post(INGEST_URL, json=payload, timeout=5)
        resp.raise_for_status()
        print(f"[web_ingestor] Ingested event for session {session_id}")
    except Exception as e:
        print(f"[web_ingestor] Failed to ingest: {e}")
