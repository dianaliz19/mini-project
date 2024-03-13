from flask import Flask, render_template
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup

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
    url='https://www.cet.ac.in/short-term-courses/'
    response = requests.get(url)
    if response.status_code == 200:
        text=response.content
        data=BeautifulSoup(text,'html.parser')
        events=data.find(id="lcp_instance_0")
        return events
    else:
        return []

def scrape_nit():
    url='https://nitc.ac.in/upcoming-events'
    response = requests.get(url)
    if response.status_code == 200:
        text=response.content
        data=BeautifulSoup(text,'html.parser')
        events=data.find(class_="xc-page-column-right")
        results=events.find(class_="xc-calendar-list")
        return results
    else:
        return []

@app.route('/')
def index():
    # Scrape events from College A and College B
    events_cet = scrape_cet()
    events_nit = scrape_nit()
    # Store the scraped events in MongoDB
    for event in events_cet:
        collection.insert_one({'college': 'Cet', 'event': event})
    for event in events_nit:
        collection.insert_one({'college': 'nit', 'event': event})
    # Retrieve the scraped events from MongoDB
    scraped_data = collection.find()
    return render_template('index.html', scraped_data=scraped_data)

if __name__ == '__main__':
    app.run(debug=True)
