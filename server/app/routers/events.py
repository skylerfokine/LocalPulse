import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi import APIRouter, HTTPException
from app.db.connection import get_connection
from app.schemas.chat import UserQuery
from app.agents.chat import chat

router = APIRouter()

@router.get("/events")
def get_events():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, title, date, time, location, description,
                   cost_free, cost_amount, category, source_url
            FROM events
            ORDER BY date ASC
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        events = []
        for row in rows:
            events.append({
                "id": str(row[0]),
                "title": row[1],
                "date": str(row[2]),
                "time": str(row[3]) if row[3] else None,
                "location": row[4],
                "description": row[5],
                "cost_free": row[6],
                "cost_amount": float(row[7]) if row[7] else None,
                "category": row[8],
                "source_url": row[9]
            })
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events/{date}")
def get_events_by_date(date: str):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, title, date, time, location, description,
                   cost_free, cost_amount, category, source_url
            FROM events
            WHERE date = %s
            ORDER BY time ASC
        """, (date,))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        events = []
        for row in rows:
            events.append({
                "id": str(row[0]),
                "title": row[1],
                "date": str(row[2]),
                "time": str(row[3]) if row[3] else None,
                "location": row[4],
                "description": row[5],
                "cost_free": row[6],
                "cost_amount": float(row[7]) if row[7] else None,
                "category": row[8],
                "source_url": row[9]
            })
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
def chat_endpoint(body: UserQuery):
    response = chat(body.question)
    return {"response": response}
