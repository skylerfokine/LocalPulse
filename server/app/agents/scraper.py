import requests
from bs4 import BeautifulSoup
from datetime import date, datetime, timezone



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
            #Ohio university Calendar URL 
            ohio_events_link = 'https://calendar.ohio.edu/calendar'
        else: 
            ohio_events_link = f'https://calendar.ohio.edu/calendar/{page}'

        links, stop = get_event_links(ohio_events_link)
        all_links.extend(links)
        page += 1
        if stop:
            break
        
    #Pass links into the event html
    return get_event_html(all_links)


def get_event_links(page_url):

    #Grabs timestamp for logging and opens file to log 
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    # Takes a listing page URL
    try: 
        ohio_events_cal = requests.get(page_url)
        ohio_events_cal.raise_for_status()
        with open("server/app/logs/scraper.log", "a") as f:
            f.write(f"{timestamp} | Scraper Agent | [PASS] | {page_url}\n")

    except  requests.exceptions.RequestException as e:
        with open("server/app/logs/scraper.log", "a") as f: 
            f.write(f"{timestamp} | Scraper Agent | [FAIL] | {page_url} | {str(e)}\n")
        return [], False

    #All the html from the ohio university calendar page
    ohio_events =  BeautifulSoup(ohio_events_cal.text, 'html.parser')

    #Variable Setup for date check
    current_month = date.today().month
    current_year = date.today().year
    now = datetime.now(timezone.utc)
    event_links = []
    stop = False
    
    #Event Population of all divs 
    events = ohio_events.find_all("div", class_="em-card") 

    #Checks Date of each card and ensures it is in same year and 
    for event in events:
        #Get our date
        time_tag = event.find("em-local-time")
        if not time_tag:
            continue
        start = time_tag.get("start")
        if not start:
            continue
        event_date = datetime.fromisoformat(start)

        #Filter the Current Month 
        if event_date.month != current_month or event_date.year != current_year:
            stop = True 
            continue

        #Filter active and non active events
        if event_date < now: 
            continue

        # Get event page Link (Use the Title link only) 
        title_link = event.find("h3", class_="em-card_title").find("a")

        if title_link:
            event_links.append(title_link["href"])

    # Returns a list of event detail URLs

    return event_links, stop

def get_event_html(events_links):
    #List to store html 
    events_html = []
    #Grabs timestamp for logging and opens file to log 
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    #fetch raw HTML for a single event detail page
    for link in events_links: 
        
        try: 
            fetch_event = requests.get(link)
            fetch_event.raise_for_status()
            with open("server/app/logs/scraper.log", "a") as f:
                f.write(f"{timestamp} | Scraper Agent | [PASS] | {link}\n")
        except  requests.exceptions.RequestException as e:
                with open("server/app/logs/scraper.log", "a") as f: 
                    f.write(f"{timestamp} | Scraper Agent | [FAIL] | {link} | {str(e)}\n")
                continue

        events_html.append(fetch_event.text)

    #All the html from the ohio university calendar page will then need passed to parser!
    return events_html

