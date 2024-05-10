from flask import Flask, render_template, request, session, url_for
from bson import ObjectId
from flask import redirect
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import bcrypt
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB configuration
MONGO_URI = 'mongodb://localhost:27017/'
DB_NAME = 'college_events'
COLLECTION_NAME = 'events'
ADMIN_COLLECTION_NAME = 'admin'
OTHER_COLLECTION_NAME = 'other_events'

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]
admin_collection = db[ADMIN_COLLECTION_NAME]
other_collection = db[OTHER_COLLECTION_NAME]

# Ensure other_events collection exists
if OTHER_COLLECTION_NAME not in db.list_collection_names():
    db.create_collection(OTHER_COLLECTION_NAME)

# Function to scrape iit palakkad
url = 'https://www.iitpkd.ac.in/past-events'

# Define the keywords to search for
keywords = ['workshop', 'lecture', 'convention', 'research']

# Function to extract text content from past events section of the webpage
def scrape_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all text siblings of elements containing "Past events"
    past_events_header = soup.find(string='Past events')

    if past_events_header:
        # Initialize a flag to indicate when to start capturing text
        capture_text = False
        text_sections = []

        # Loop through the siblings of the past events header
        for sibling in past_events_header.find_all_next(string=True):
            # Check if the sibling is a tag
            if sibling.name:
                # Check if the sibling is pagination section
                if sibling.get('id') == 'table-pagination':
                    break  # Stop capturing text if pagination section is encountered
            else:
                # Capture the text if not pagination section
                for keyword in keywords:
                    if keyword in sibling.lower():
                        text_sections.append(sibling.strip())
                        break  # Once a keyword is found, move to the next sibling

        return text_sections
    else:
        return []

def scrape_nitRaipur():
    url = 'https://nitrr.ac.in/conferences.php'
    try:
        response = requests.get(url, timeout=5)  # Set a timeout to prevent hanging
        if response.status_code == 200:
            text = response.content
            data = BeautifulSoup(text, 'html.parser')
            events_container = data.find(id="datacontainer")
            event_text = events_container.get_text().strip()
            events = [' '.join(event.split()) for event in event_text.split('\n') if event.strip()]
            return events
        else:
            return "Site Down"
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return "Site Down"

def scrape_nitNagpur():
    url = 'https://vnit.ac.in/category/events/'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            text = response.content
            data = BeautifulSoup(text, 'html.parser')
            events = data.find_all(class_="entry-article-part entry-article-header")
            event_list = []
            for event in events:
                results = event.find(class_="entry-title entry--item")
                event_text = results.get_text()
                cleaned_event = ' '.join(event_text.split())
                event_list.append(cleaned_event)
            return event_list
        else:
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return "Site Down"
    
def scrape_nitSurathkal():
    url = 'https://www.nitk.ac.in/upcoming_events'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            text = response.content
            data = BeautifulSoup(text, 'html.parser')
            events = data.find_all(class_="gdlr-core-event-item-content-wrap")
            event_list = []
            for event in events:
                event_text = event.get_text().strip()
                event_list.append(event_text)
            return event_list
        else:
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return "Site Down"

def scrape_cusat():
    url = 'https://www.cusat.ac.in/events'
    try:
        response = requests.get(url, timeout=5)  # Set a timeout to prevent hanging
        if response.status_code == 200:
            text = response.content
            data = BeautifulSoup(text, 'html.parser')
            data = BeautifulSoup(text, 'html.parser')
            events = data.find("div", class_="ed-about-tit")
            item=[]
            if events:
                event_text = events.get_text().strip()
                # Split the event text by newline character to identify separate events
                events_list = event_text.split('\n')
                current_event = ""
                for event in events_list[1:]:
                    event = ' '.join(event.split())  # Remove extra whitespaces
                    if event:  # Check if event is not empty
                        if event.isdigit() or event.startswith("Read more"):
                            continue  # Skip event dates and "Read more" lines
                        else:
                            #print(event)  # Print event title
                            item.append(event)
            else:
                print("No events found")
            return item
        else:
            return "Site Down"
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return "Site Down"

def scrape_nit():
    url = 'https://nitc.ac.in/upcoming-events'
    try:
        response = requests.get(url, timeout=5)  # Set a timeout to prevent hanging
        if response.status_code == 200:
            text = response.content
            data = BeautifulSoup(text, 'html.parser')
            events = data.find(class_="xc-page-column-right")
            results = events.find(class_="xc-calendar-list")
            event_text = results.get_text(separator='\n')
            return event_text.strip()
        else:
            return "Site Down"
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return "Site Down"

def scrape_iitbhu():
    url = 'https://www.iitbhu.ac.in/events'
    response = requests.get(url)
    if response.status_code == 200:
        text = response.content
        data = BeautifulSoup(text, 'html.parser')
        events = data.find_all(class_="text-align-justify")
        event_list = []
        for event in events:
            event_text = event.get_text().strip()
            event_list.append(event_text)
        return event_list
    else:
        return []

def scrape_nitTrichy():
    url = 'https://www.nitt.edu/home/academics/departments/meta/events/workshops/'
    try:
        response = requests.get(url, timeout=5)  # Set a timeout to prevent hanging
        if response.status_code == 200:
            text = response.content
            data = BeautifulSoup(text, 'html.parser')
            events_container = data.find("div", id="contentcontainer")
            if events_container:
                event_elements = events_container.find_all("li")
                event_text = [event.get_text(strip=True) for event in event_elements]
                for i in range(len(event_text)):
                    event_text[i] = ' '.join(event_text[i].split())
                return event_text
            else:
                return "No events found on the page"
        else:
            return "Site Down"
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return "Site Down"

def scrape_nitJaipur():
    url = 'https://mnit.ac.in/news/newsall?type=event'
    response = requests.get(url)
    if response.status_code == 200:
        text = response.content
        data = BeautifulSoup(text, 'html.parser')
        event_list = []
        event_divs = data.find_all(id="pills-2")
        for div in event_divs:
            event_tags = div.find_all('a')
            for event in event_tags:
                event_text = event.get_text().strip()
                event_list.append(event_text)
        return event_list
    else:
        return []

def scrape_cet():
    url = 'https://www.cet.ac.in/short-term-courses/'
    try:
        response = requests.get(url, timeout=5)  # Set a timeout to prevent hanging
        if response.status_code == 200:
            text = response.content
            data = BeautifulSoup(text, 'html.parser')
            events = data.find(id="lcp_instance_0")
            event_text = events.get_text(separator='\n')
            return event_text.strip()
        else:
            return "Site Down"
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return "Site Down"


@app.route('/')
def index():
    # Retrieve the scraped events from MongoDB
    scraped_data = collection.find_one({}, {'_id': 0})
    if scraped_data is None:
        scraped_data = {}

    return render_template('index.html', scraped_data=scraped_data)


@app.route('/event-details')
def event_details():
    collection.delete_many({})
    # Scrape events from College A and College B
    events_iit = scrape_data(url)
    events_nitTrichy = scrape_nitTrichy()
    events_nitNagpur = scrape_nitNagpur()
    events_cusat = scrape_cusat()
    events_nit = scrape_nit()
    events_nitRaipur = scrape_nitRaipur()
    events_nitSurathkal = scrape_nitSurathkal()
    events_cet = scrape_cet()
    events_nitJaipur = scrape_nitJaipur()
    events_iitbhu = scrape_iitbhu()

    # Store the scraped events in MongoDB
    college_data = [
        {'college': 'IIT Palakkad', 'url': 'https://www.iitpkd.ac.in/past-events', 'events': events_iit},
        {'college': 'NIT Trichy','url': 'https://www.nitt.edu/home/academics/departments/meta/events/workshops/','events': events_nitTrichy},
        {'college': 'NIT Nagpur', 'url': 'https://vnit.ac.in/category/events/', 'events': events_nitNagpur},
        {'college': 'CUSAT', 'url': 'https://www.cusat.ac.in/events', 'events': events_cusat},
        {'college': 'NIT Jaipur', 'url': 'https://mnit.ac.in/news/newsall?type=event', 'events': events_nitJaipur},
        {'college': 'NIT Calicut', 'url': 'https://nitc.ac.in/upcoming-events', 'events': events_nit.split('\n')},
        {'college': 'NIT Surathkal', 'url': 'https://www.nitk.ac.in/upcoming_events', 'events': events_nitSurathkal},
        {'college': 'NIT Raipur', 'url': 'https://nitrr.ac.in/', 'events': events_nitRaipur},
        {'college': 'CET', 'url': 'https://www.cet.ac.in/short-term-courses/', 'events': events_cet.split('\n')},
        {'college': 'IIT Bhuvaneshvar', 'url': 'https://www.iitbhu.ac.in/events', 'events': events_iitbhu}
    ]


    collection.insert_one({'colleges': college_data})

    # Retrieve the scraped events from MongoDB
    scraped_data = collection.find_one({}, {'_id': 0})

    # Retrieve other events from other_collection
    other_events = other_collection.find()

    print("Scraped data:", scraped_data)  # Print scraped data for debugging

    return render_template('event-details.html', scraped_data=scraped_data, other_events=other_events)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/demo')
def demo():
    return render_template('demo.html')


# Admin login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin = admin_collection.find_one({'username': username})

        if admin:
            if bcrypt.checkpw(password.encode('utf-8'), admin['password']):
                session['admin_id'] = str(admin['_id'])
                return redirect(url_for('dashboard'))

        # Login failed
        return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')


# Admin logout route
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))

# Admin registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    session.clear()
    return redirect(url_for('register_admin'))

# Admin dashboard route
@app.route('/dashboard')
def dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    # Fetch events from the main events collection
    events_main = collection.find()

    # Fetch events from the other_events collection
    other_events = other_collection.find()

    return render_template('dashboard.html', events_main=events_main, other_events=other_events)



# Add event route (for admins only)
@app.route('/add_event', methods=['POST'])
def add_event():
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        college = request.form['college']
        event_name = request.form['event_name']

        if not college or not event_name:
            return "Error: College and event name are required fields"

        other_collection.update_one({'college': college}, {'$push': {'events': event_name}}, upsert=True)

        return redirect(url_for('dashboard'))
    else:
        return "Error: Method not allowed"


# Delete event route (for admins only)
@app.route('/delete_event', methods=['POST'])
def delete_event():
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Retrieve the event ID from the form data
        event_id = request.form.get('event_id')

        # Validate event_id
        try:
            event_id = ObjectId(event_id)
        except Exception as e:
            print("Invalid event ID:", e)
            return "Invalid event ID"

        # Try to delete the event from the other_events collection
        try:
            result = other_collection.delete_one({'_id': event_id})
            if result.deleted_count == 1:
                print("Event deleted successfully")
            else:
                print("Event not found or not deleted")
            return redirect(url_for('dashboard'))
        except Exception as e:
            print("Error deleting event:", e)
            return "Error deleting event. Please try again later."

    # If accessed via GET request, redirect back to the dashboard
    return redirect(url_for('dashboard'))


# Register admin route (optional)
@app.route('/register_admin', methods=['GET', 'POST'])
def register_admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if username already exists
        if admin_collection.find_one({'username': username}):
            return render_template('register_admin.html', error='Username already exists')

        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert admin into database
        admin_collection.insert_one({'username': username, 'password': hashed_password})
        return redirect(url_for('login'))

    return render_template('register_admin.html')


if __name__ == '__main__':
    app.run(debug=True)
