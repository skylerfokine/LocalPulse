import os 
import sys 
import json 
import requests
from datetime import date, timedelta

#Create one clean path for the file so it can acesses things in other directorys 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from app.agents.parser import OLLAMA_URL
from app.db.connection import get_connection

CHAT_LOG = os.path.join(os.path.dirname(__file__), "..", "logs", "chat.log")
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"


def chat(user_query: str) -> str:
    #Pull the next 7 days of events from the import from the db 
    conn = get_connection()
    cur = conn.cursor()
    today = date.today()
    week_out = today + timedelta(days = 7)
    cur.execute("""
                SELECT title,date,time,cost_free,cost_amount, location, source url
                FROM events
                WHERE date >= %s AND date <= %s
                ORDER BY date ASC, time ASC
                """, (today, week_out))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    #format events into readable string for a prompt 
    if now rows: 
        return "I dont see any upcoming events in the next 7 days."

    event_lines = []
    for row in rows: 
        title, evt_date, evt_time, cost_free, cost_amount, location, source_url = row 
        cost_str = "Free" if cost_free else (f"${cost_amount}" if cost_amount else "N/A")
        time_str =  str(evt_time) if evt_time else "Time TBD"
        loc_str = location if location else "location TBD"
        event_lines.append(
                f"- {title} | {evt_date} {time_str} | {loc_str} | {cost_str} | {source_url} "
                )
        events_block = "\n".join(event_lines)

    # Build prompt
    prompt = f"""You are a friendly local events assistant for Athens, Ohio.
Here are the upcoming events in the next 7 days:

{events_block}

User question: {user_query}

Answer helpfully and conversationally. Reference specific events by name when relevant. Keep it concise."""

    # Call Qwen via Ollama
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": "qwen2.5-coder:7b",
            "prompt": prompt,
            "stream": False
        })
        response.raise_for_status()
        answer = response.json().get("response", "").strip()
    except Exception as e:
        with open(CHAT_LOG, "a") as f:
            f.write(f"[FAIL] Chat query failed | {str(e)}\n")
        return "Sorry, I couldn't process your question right now."

    #Log and return
    with open(CHAT_LOG, "a") as f:
        f.write(f"[PASS] Query: {user_query}\n")

    return answer

