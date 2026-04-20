import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import uuid
from datetime import datetime
from app.db.connection import get_connection

def insert_event(event):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO events (
                id, title, date, time, location, description,
                cost_free, cost_amount, category, source_url, scraped_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            str(uuid.uuid4()),
            event.get("title"),
            event.get("date"),
            event.get("time") if event.get("time") != "N/A" else None,
            event.get("location") if event.get("location") != "N/A" else None,
            event.get("description") if event.get("description") != "N/A" else None,
            event.get("cost_free"),
            event.get("cost_amount"),
            event.get("category") if event.get("category") != "N/A" else None,
            event.get("source_url"),
            datetime.now()
        ))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Insert error: {e}")
        return False

if __name__ == "__main__":
    test_event = {
        "title": "Test Event",
        "date": "2026-04-25",
        "time": "17:00",
        "location": "Athens, OH",
        "description": "A test event",
        "cost_free": True,
        "cost_amount": None,
        "category": "community",
        "source_url": "https://example.com/test"
    }
    result = insert_event(test_event)
    print("Inserted:" if result else "Failed")
