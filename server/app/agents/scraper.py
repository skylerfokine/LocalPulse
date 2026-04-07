import requests
from bs4 import BeautifulSoup


# Urls 
ohio_events_cal = requests.get('https://calendar.ohio.edu/calendar')

ohio_events =  BeautifulSoup(ohio_events_cal, 'html.parser')

def get_event_links(page_url):
    # Takes a listing page URL
    # Returns a list of event detail URLs

