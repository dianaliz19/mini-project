from flask import Flask, render_template
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
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
    # Initialize Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver = webdriver.Chrome('./chromedriver')
    driver.get('https://www.cet.ac.in/short-term-courses/')
    driver.maximize_window()
    time.sleep(5)
    initial_snapshot = driver.page_source

    # Main loop
    refresh_seconds = 60  # seconds
    while True:
        time.sleep(refresh_seconds)
        driver.refresh()
        new_snapshot = driver.page_source
        if new_snapshot != initial_snapshot:
            initial_snapshot = new_snapshot  # Update the snapshot for the next iteration

            # Scrape events from College A and College B
            events_cet = scrape_cet()
            events_nit = scrape_nit()
            print("CET events:", events_cet)
            print("NIT events:", events_nit)

            # Update the scraped events in MongoDB
            collection.update_one({'college': 'Cet'}, {'$set': {'events': events_cet.split('\n')}})
            collection.update_one({'college': 'nit'}, {'$set': {'events': events_nit.split('\n')}})

            # Retrieve the updated scraped events from MongoDB
            scraped_data = collection.find({}, {'_id': 0})
            return render_template('index.html', scraped_data=scraped_data)

if __name__ == '__main__':
    app.run(debug=True)
