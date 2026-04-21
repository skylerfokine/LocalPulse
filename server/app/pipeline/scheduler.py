import os
import sys
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from apscheduler.schedulers.blocking import BlockingScheduler
from app.agents.scraper import scrape
from app.agents.parser import parse
from app.agents.validator import validate
from app.db.insert import insert_event

GOLD_STANDARD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "tests", "gold_standard", "input")
GOLD_STANDARD_SAVED = False

def save_gold_standard(scraped):
    global GOLD_STANDARD_SAVED
    if GOLD_STANDARD_SAVED:
        return
    os.makedirs(GOLD_STANDARD_DIR, exist_ok=True)
    for i, (url, source, trimmed_dict) in enumerate(scraped[:20]):
        filepath = os.path.join(GOLD_STANDARD_DIR, f"event_{i+1}.json")
        with open(filepath, "w") as f:
            json.dump({"url": url, "source": source, "trimmed_dict": trimmed_dict}, f, indent=2)
    print(f"Saved {min(20, len(scraped))} gold standard input files.")
    GOLD_STANDARD_SAVED = True

def run_pipeline():
    print("Pipeline started...")
    sources = ['ohiouni', 'stuarts']
    for source in sources:
        print(f"Scraping {source}...")
        scraped = scrape(source)
        save_gold_standard(scraped)
        print(f"Parsing {len(scraped)} events from {source}...")
        parsed = parse(scraped)
        print(f"Validating {len(parsed)} events...")
        validated = validate(parsed)
        for event in validated:
            insert_event(event)
        print(f"Inserted {len(validated)} events from {source}")
    print("Pipeline complete.") 

if __name__ == "__main__":
    run_pipeline()
    scheduler = BlockingScheduler()
    scheduler.add_job(run_pipeline, 'cron', hour=6)
    scheduler.start()
