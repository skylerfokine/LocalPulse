import requests
from bs4 import BeautifulSoup

def get_event_links(events):
    # Takes a listing page URL
    # Returns a list of event detail URLs
    print("hello world")


#Ohio university Calendar URL 
ohio_events_cal = requests.get('https://calendar.ohio.edu/calendar')


#All the html from the ohio university calendar page
ohio_events =  BeautifulSoup(ohio_events_cal.text, 'html.parser')


