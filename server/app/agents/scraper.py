import os  
import requests
from bs4 import BeautifulSoup
from datetime import date, datetime, timezone

# single constant for log path, works regardless of working directory
SCRAPER_LOG = os.path.join(os.path.dirname(__file__), "..", "logs", "scraper.log")

def scrape(url): 
    if url == 'ohiouni': 
        return scrape_ohio_events()
    else: 
        pass

def scrape_ohio_events():
    #paginates, calls both functions, returns a list of raw HTML strings
    page = 1
    all_links = []
    while True: 
        if page == 1: 
            ohio_events_link = 'https://calendar.ohio.edu/calendar'
        else: 
            ohio_events_link = f'https://calendar.ohio.edu/calendar/{page}'
        links, stop = get_event_links(ohio_events_link)
        all_links.extend(links)
        page += 1
        if stop:
            break
    return get_event_html(all_links)

def get_event_links(page_url):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    try: 
        ohio_events_cal = requests.get(page_url)
        ohio_events_cal.raise_for_status()
        with open(SCRAPER_LOG, "a") as f:  
            f.write(f"{timestamp} | Scraper Agent | [PASS] | {page_url}\n")
    except requests.exceptions.RequestException as e:
        with open(SCRAPER_LOG, "a") as f:  
            f.write(f"{timestamp} | Scraper Agent | [FAIL] | {page_url} | {str(e)}\n")
        return [], False

    ohio_events = BeautifulSoup(ohio_events_cal.text, 'html.parser')
    current_month = date.today().month
    current_year = date.today().year
    now = datetime.now(timezone.utc)
    event_links = []
    stop = False

    events = ohio_events.find_all("div", class_="em-card") 
    for event in events:
        time_tag = event.find("em-local-time")
        if not time_tag:
            continue
        start = time_tag.get("start")
        if not start:
            continue
        event_date = datetime.fromisoformat(start)
        if event_date.month != current_month or event_date.year != current_year:
            stop = True 
            continue
        if event_date < now: 
            continue
        title_link = event.find("h3", class_="em-card_title").find("a")
        if title_link:
            event_links.append(title_link["href"])
    return event_links, stop

def get_event_html(events_links):
    events_html = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    for link in events_links: 
        try: 
            fetch_event = requests.get(link)
            fetch_event.raise_for_status()
            with open(SCRAPER_LOG, "a") as f:  
                f.write(f"{timestamp} | Scraper Agent | [PASS] | {link}\n")
        except requests.exceptions.RequestException as e:
            with open(SCRAPER_LOG, "a") as f:  
                f.write(f"{timestamp} | Scraper Agent | [FAIL] | {link} | {str(e)}\n")
            continue
        events_html.append(fetch_event.text)
    return events_html

if __name__ == "__main__": 
    links, stop = get_event_links('https://calendar.ohio.edu/calendar')
    html = get_event_html(links[:1])
    print(html[0])
