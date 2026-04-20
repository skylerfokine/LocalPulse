import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from apscheduler.schedulers.blocking import BlockingScheduler
from app.agents.scraper import scrape
from app.agents.parser import parse
from app.agents.validator import validate
from app.db.insert import insert_event

def run_pipeline():
    print("Pipeline started...")
    sources = ['ohiouni', 'stuarts']
    for source in sources:
        print(f"Scraping {source}...")
        scraped = scrape(source)
        print(f"Parsing {len(scraped)} events from {source}...")
        parsed = parse(scraped)
        print(f"Validating {len(parsed)} events...")
        validated = validate(parsed)
        for event in validated:
            insert_event(event)
        print(f"Inserted {len(validated)} events from {source}")
    print("Pipeline complete.")

if __name__ == "__main__":
    # Run once immediately for testing
    run_pipeline()

    # Then schedule daily at 6am
    scheduler = BlockingScheduler()
    scheduler.add_job(run_pipeline, 'cron', hour=6)
    scheduler.start()
