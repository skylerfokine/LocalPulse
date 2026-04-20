import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "qwen2.5-coder:7b"
PARSER_LOG = os.path.join(os.path.dirname(__file__), "..", "logs", "parser.log")

def parse(scraped_events):
    results = []
    for url, source, fields in scraped_events:
        event = parse_event(url, source, fields)
        if event:
            results.append(event)
    return results

def parse_event(url, source, fields):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Strip HTML tags from each field value
    clean = {}
    for key, val in fields.items():
        if val:
            clean[key] = BeautifulSoup(val, "html.parser").get_text(separator=" ", strip=True)
        else:
            clean[key] = "N/A"

    prompt = f"""You are a data extraction assistant. Extract event information from the following data and return ONLY a valid JSON object with no explanation, no markdown, no code fences.

Use exactly these field names and types:
- "title": string
- "date": string in YYYY-MM-DD format
- "time": string in HH:MM 24hr format, or "N/A" if not found
- "location": string, or "N/A" if not found
- "description": string, or "N/A" if not found
- "cost_free": boolean (true if free, false if paid, null if unknown)
- "cost_amount": number in dollars, or null if free or unknown
- "category": one of "campus", "community", "theater", "concert", or "N/A" if unclear
- "source_url": "{url}"

Event data:
title: {clean.get('title', 'N/A')}
date: {clean.get('date', 'N/A')}
time: {clean.get('time', 'N/A')}
location: {clean.get('location', 'N/A')}
description: {clean.get('description', 'N/A')}

Return ONLY the JSON object. No other text."""

    raw = call_ollama(prompt)
    if raw is None:
        with open(PARSER_LOG, "a") as f:
            f.write(f"{timestamp} | Parser Agent | [FAIL] | {url} | Ollama call failed\n")
        return None

    event = try_parse_json(raw)
    if event is None:
        # Reprompt once asking it to clean up
        retry_prompt = f"Return this as valid JSON only, no markdown, no explanation:\n{raw}"
        raw2 = call_ollama(retry_prompt)
        if raw2:
            event = try_parse_json(raw2)

    if event is None:
        with open(PARSER_LOG, "a") as f:
            f.write(f"{timestamp} | Parser Agent | [FAIL] | {url} | JSON parse failed after retry\n")
        return None

    with open(PARSER_LOG, "a") as f:
        f.write(f"{timestamp} | Parser Agent | [PASS] | {url} | title: {event.get('title', 'N/A')}\n")

    return event

def call_ollama(prompt):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        return None

def try_parse_json(text):
    # Strip markdown fences if present
    cleaned = text.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None

if __name__ == "__main__":
    from scraper import get_stuarts_links, get_event_html
    links, stop = get_stuarts_links('https://stuartsoperahouse.org/events/')
    scraped = get_event_html(links[:1], 'stuarts')
    results = parse(scraped)
    print(json.dumps(results, indent=2))
