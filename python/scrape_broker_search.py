import os
import json
from curl_cffi import requests

# --- Configuration ---
BASE_URL = "https://www.idx.co.id/primary"
BROKER_SEARCH_ENDPOINT = "/ExchangeMember/GetBrokerSearch?option=0&license=&start=0&length=9999"

# Headers (reusing from previous scripts)
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "Referer": "https://www.idx.co.id/id/members-and-participants/exchange-member-directory/" 
}

# File Paths (relative to the python/ directory)
DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')
OUTPUT_FILE = os.path.join(DATA_DIR, 'brokerSearch.json')

# --- Utility Functions ---

def ensure_data_dir():
    """Ensures the data directory exists."""
    os.makedirs(DATA_DIR, exist_ok=True)

def fetch_data(url):
    """Generic function to fetch data from a given URL."""
    print(f"Fetching {url}...")
    try:
        response = requests.get(
            url, 
            headers=HEADERS, 
            impersonate="chrome",
            timeout=30
        )
        
        status_code = response.status_code
        print(f"Status Code: {status_code}")
        
        if status_code == 200:
            try:
                data = response.json()
                print("Successfully parsed JSON.")
                return data
            except json.JSONDecodeError:
                print(f"Failed to decode JSON. Snippet: {response.text[:500]}")
        else:
            print(f"Request failed. Snippet: {response.text[:500]}")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        
    return None

def save_json(file_path, data):
    """Saves data to a JSON file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Broker search data saved to {os.path.basename(file_path)}")
    except IOError as e:
        print(f"Error saving data to {file_path}: {e}")

# --- Main Scraper ---

def scrape_broker_search():
    """Fetches broker search data and saves the result."""
    ensure_data_dir()
    
    url = f"{BASE_URL}{BROKER_SEARCH_ENDPOINT}"
    
    data = fetch_data(url)
    
    if data:
        save_json(OUTPUT_FILE, data)
    else:
        print("Failed to collect broker search data. No file saved.")

if __name__ == "__main__":
    scrape_broker_search()