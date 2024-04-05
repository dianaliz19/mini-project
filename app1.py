from flask import Flask, render_template
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import schedule
import time

app = Flask(__name__)

# MongoDB configuration
MONGO_URI = 'mongodb://localhost:27017/'
DB_NAME = 'college_events_db'
COLLECTION_NAME = 'events'

# Initialize MongoDB client and collection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Function to scrape events from College A website
def scrape_cet():
    url = 'https://www.cet.ac.in/short-term-courses/'
    response = requests.get(url)
    if response.status_code == 200:
        text = response.content
        data = BeautifulSoup(text, 'html.parser')
        events = data.find(id="lcp_instance_0")
        event_text = events.get_text(separator='\n')
        return event_text.strip()
    else:
        return []

def scrape_nit():
    url = 'https://nitc.ac.in/upcoming-events'
    response = requests.get(url)
    if response.status_code == 200:
        text = response.content
        data = BeautifulSoup(text, 'html.parser')
        events = data.find(class_="xc-page-column-right")
        results = events.find(class_="xc-calendar-list")
        event_text = results.get_text(separator='\n')
        return event_text.strip()
    else:
        return []

def scrape_iitb():
    url = 'https://www.iitb.ac.in/events'
    response = requests.get(url)
    if response.status_code == 200:
        text = response.content
        data = BeautifulSoup(text, 'html.parser')
        events = data.find(class_="fc-list-table")
        results = events.find(class_="fc-list-item fc-has-url")
        event_text = results.get_text(separator='\n')
        return event_text.strip()
    else:
        return []

# Function to scrape events from all college websites and update MongoDB
def scrape_and_update():
    collection.delete_many({})
    events_cet = scrape_cet()
    events_nit = scrape_nit()
    #events_iitb = scrape_iitb()
    print("CET events:", events_cet)
    print("NIT events:", events_nit)
    #print("IITB events:", events_iitb)
    collection.insert_one({'college': 'Cet', 'events': events_cet.split('\n')})
    collection.insert_one({'college': 'nit', 'events': events_nit.split('\n')})
    #collection.insert_one({'college': 'iitb', 'events': events_iitb.split('\n')})
    print("Events scraped and updated in MongoDB")

# Schedule the scraping and updating task to run every 60 seconds
schedule.every(60).seconds.do(scrape_and_update)

# Flask route to render the index.html template with scraped data
@app.route('/')
def index():
    scraped_data = collection.find({}, {'_id': 0})
    return render_template('event_details.html', scraped_data=scraped_data)

if __name__ == '__main__':
    # Run the Flask application
    app.run(debug=True)  # Start the Flask server
