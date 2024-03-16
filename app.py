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
        event_text = events.get_text(separator='\n')
        return event_text.strip()
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
        event_text = results.get_text(separator='\n')
        return event_text.strip()
    else:
        return []

@app.route('/')
def index():
    collection.delete_many({})
    # Scrape events from College A and College B
    events_cet = scrape_cet()
    events_nit = scrape_nit()
    print("CET events:", events_cet)
    print("NIT events:", events_nit)
    # Store the scraped events in MongoDB
    collection.insert_one({'college': 'Cet', 'events': events_cet.split('\n')})
    collection.insert_one({'college': 'nit', 'events': events_nit.split('\n')})
    # Retrieve the scraped events from MongoDB
    scraped_data = collection.find({},{'_id':0})
    return render_template('index.html', scraped_data=scraped_data)

if __name__ == '__main__':
    app.run(debug=True)
