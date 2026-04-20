import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from datetime import date, datetime
from app.db.connection import get_connection

VALIDATOR_LOG = os.path.join(os.path.dirname(__file__), "..", "logs", "validator.log")

def validate(parsed_events):
    results = []
    for event in parsed_events:
        validated = validate_event(event)
        if validated:
            results.append(validated)
    return results

def validate_event(event):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    url = event.get("source_url", "unknown")

    # Check required fields
    for field in ["title", "date", "source_url"]:
        if not event.get(field):
            with open(VALIDATOR_LOG, "a") as f:
                f.write(f"{timestamp} | Validator Agent | [FAIL] | {url} | missing required field: {field}\n")
            return None

    # Check event is not in the past
    try:
        event_date = date.fromisoformat(event["date"])
        if event_date < date.today():
            with open(VALIDATOR_LOG, "a") as f:
                f.write(f"{timestamp} | Validator Agent | [FAIL] | {url} | past event: {event['date']}\n")
            return None
    except ValueError:
        with open(VALIDATOR_LOG, "a") as f:
            f.write(f"{timestamp} | Validator Agent | [FAIL] | {url} | invalid date format: {event['date']}\n")
        return None

    # Check for duplicates
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM events WHERE title = %s AND date = %s AND location = %s",
            (event.get("title"), event.get("date"), event.get("location"))
        )
        if cur.fetchone():
            with open(VALIDATOR_LOG, "a") as f:
                f.write(f"{timestamp} | Validator Agent | [FAIL] | {url} | duplicate event\n")
            return None
        cur.close()
        conn.close()
    except Exception as e:
        with open(VALIDATOR_LOG, "a") as f:
            f.write(f"{timestamp} | Validator Agent | [FAIL] | {url} | DB error: {str(e)}\n")
        return None

    with open(VALIDATOR_LOG, "a") as f:
        f.write(f"{timestamp} | Validator Agent | [PASS] | {url}\n")

    return event


if __name__ == "__main__":
    test_event = {
        "title": "Nelsonville Music Festival Party at Jackie O's On Fourth",
        "date": "2026-04-25",
        "time": "17:00",
        "location": "Jackie Os on 4th",
        "description": "Test event",
        "cost_free": True,
        "cost_amount": None,
        "category": "community",
        "source_url": "https://stuartsoperahouse.org/events/test"
    }
    result = validate_event(test_event)
    print(result)
