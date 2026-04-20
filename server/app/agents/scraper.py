import os  
import requests
from bs4 import BeautifulSoup
from datetime import date, datetime, timezone

# single constant for log path, works regardless of working directory
SCRAPER_LOG = os.path.join(os.path.dirname(__file__), "..", "logs", "scraper.log")

def scrape(url): 
    if url == 'ohiouni': 
        return scrape_ohio_events()
    elif url == 'stuarts': 
        return scrape_stuarts()

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
    return get_event_html(all_links, 'ohiouni' )

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

def get_event_html(events_links, source):
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

        soup = BeautifulSoup(fetch_event.text, 'html.parser')

        if source == 'ohiouni':
            fields = {
                'title': soup.find("h1", class_="em-header-card_title"),
                'date': soup.find("p", class_="em-date"),
                'cost': soup.find("span", class_="em-price-tag"),
                'description': soup.find("div", class_="em-about_description"),
            }
        elif source == 'stuarts':
            fields = {
                'title': soup.find("h1", class_="page-title"),
                'date': soup.find("span", class_="event-info-content event-date"),
                'time': soup.find("span", class_="event-info-content event-time"),
                'location': soup.find("span", class_="event-info-content event-location"),
                'description': soup.find("div", class_="single-event-description"),
             }
        else:
            with open(SCRAPER_LOG, "a") as f:
                f.write(f"{timestamp} | Scraper Agent | [FAIL] | {link} | unknown source: {source}\n")
            continue

        trimmed = {k: str(v) if v else None for k, v in fields.items()}
        events_html.append((link, source, trimmed))

    return events_html

def scrape_stuarts():
    page = 1
    all_links = []
    while True:
        if page == 1:
            stuarts_url = 'https://stuartsoperahouse.org/events/'
        else:
            stuarts_url = f'https://stuartsoperahouse.org/events/?pno={page}'
        links, stop = get_stuarts_links(stuarts_url)
        all_links.extend(links)
        page += 1
        if stop:
            break
    return get_event_html(all_links, 'stuarts')

def get_stuarts_links(page_url):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    try:
        response = requests.get(page_url)
        response.raise_for_status()
        with open(SCRAPER_LOG, "a") as f:
            f.write(f"{timestamp} | Scraper Agent | [PASS] | {page_url}\n")
    except requests.exceptions.RequestException as e:
        with open(SCRAPER_LOG, "a") as f:
            f.write(f"{timestamp} | Scraper Agent | [FAIL] | {page_url} | {str(e)}\n")
        return [], False

    soup = BeautifulSoup(response.text, 'html.parser')
    current_month = date.today().month
    current_year = date.today().year
    event_links = []
    stop = False

    cards = soup.find_all("div", class_="event cf")
    for card in cards:
        # Parse date from event-when field e.g. "Saturday, Apr 25th, 2026"
        when = card.find("p", class_="event-when event-field")
        if not when:
            continue
        date_text = when.get_text(" ", strip=True)
        # Strip ordinal suffixes so strptime can parse it
        date_text = date_text.replace("th,", ",").replace("st,", ",").replace("nd,", ",").replace("rd,", ",")
        try:
            date_part = date_text.split("Date:")[-1].split("|")[0].strip()
            event_date = datetime.strptime(date_part, "%A, %b %d, %Y")
        except ValueError:
            continue
        if event_date.month != current_month or event_date.year != current_year:
            stop = True
            continue
        # Get event detail link from the "More Info" button
        buttons_div = card.find("div", class_="event-buttons")
        if not buttons_div:
            continue
        link_tag = buttons_div.find("a")
        if link_tag and link_tag.get("href"):
            href = link_tag["href"]
            if href.startswith("/"):
                href = "https://stuartsoperahouse.org" + href
            event_links.append(href)

    return event_links, stop

#if __name__ == "__main__": 
#    links, stop = get_event_links('https://calendar.ohio.edu/calendar')
#    html = get_event_html(links[:1])
#    print(html[0])

if __name__ == "__main__":
    links, stop = get_stuarts_links('https://stuartsoperahouse.org/events/')
    html = get_event_html(links[:1], 'stuarts')
    print(html[0])


