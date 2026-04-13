import requests
from bs4 import BeautifulSoup
form datetime import date

def scrape_ohio_events():
    #paginates, calls both functions, returns a list of raw HTML strings
    first_of_next_month = calculate_first_of_next_month() 
    page = 1
    all_links = []
    while True: 
        links, stop = get_event_links(ohio_events_cal)
        all_links.extend(links)
        page += 1
        if stop:
            break
        
    #Pass links into the event html
    events =get_event_html(links)


def get_event_links(page_url):
    # Takes a listing page URL
    #checks date of last card in request
    # Returns a list of event detail URLs


def get_event_html(events_url):
    #fetch raw HTML for a single event detail page

def calculate_first_of_next_month(): 
    today = date.today()

    if today.month == 12:
        first_of_next_month = date(today.year + 1, 1, 1)
    else: 
        first_of_next_month = date (today.year, today.month + 1, 1)
    return first_of_next_month


#Ohio university Calendar URL 
ohio_events_cal = requests.get('https://calendar.ohio.edu/calendar')

#All the html from the ohio university calendar page
ohio_events =  BeautifulSoup(ohio_events_cal.text, 'html.parser')


