import os
import time
import json
import sys
from datetime import datetime
from urllib.parse import urlencode
from curl_cffi import requests

# --- Configuration ---
BASE_URL = "https://www.idx.co.id/secondary/get/StructuredWarrant/Information"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "referer": "https://www.idx.co.id/id/data-pasar/structured-warrant-sw/informasi-structured-warrant"
}

# File Paths (relative to the python/ directory)
DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')
OUTPUT_FILE = os.path.join(DATA_DIR, 'structured_warrants.json')

# Rate limiting/error handling constants
RATE_LIMIT_SLEEP_SECONDS = 30
MAX_RETRIES = 3

# --- Utility Functions ---

def ensure_data_dir():
    """Ensures the data directory exists."""
    os.makedirs(DATA_DIR, exist_ok=True)

def fetch_data(url, params=None):
    """Generic function to fetch data from a given URL using curl_cffi."""
    try:
        response = requests.get(
            url,
            params=params,
            headers=HEADERS,
            impersonate="chrome",
            timeout=60
        )

        status_code = response.status_code

        if status_code == 200:
            try:
                data = response.json()
                print(f"Status: {status_code}. Successfully parsed JSON.")
                return data
            except json.JSONDecodeError:
                print(f"Status: {status_code}. Failed to decode JSON. Snippet: {response.text[:500]}")
        elif status_code == 429:
            print(f"Status: {status_code}. Rate limit hit.")
            raise requests.RequestsError("Rate Limit (429) Hit")
        else:
            print(f"Status: {status_code}. Request failed. Snippet: {response.text[:500]}")

    except requests.RequestsError as e:
        if "Rate Limit (429) Hit" in str(e):
            raise
        print(f"A request error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return None

def save_json(file_path, data):
    """Saves data to a JSON file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Successfully saved data to {os.path.basename(file_path)}")
    except IOError as e:
        print(f"Error saving data to {file_path}: {e}")

# --- Main Scraper ---

def scrape_structured_warrants():
    """Fetches all structured warrant data and saves the result.

    The IDX structured warrant API requires start/length query parameters
    but returns all records regardless of their values (no server-side pagination).
    We pass start=0&length=9999 to request all records in a single call.
    """
    ensure_data_dir()

    retries = 0
    data = None
    params = {"start": 0, "length": 9999}

    print("Starting structured warrant data collection...")

    while retries <= MAX_RETRIES:
        try:
            print(f"Fetching all structured warrant records...")
            data = fetch_data(BASE_URL, params=params)

            if data and data.get('Results'):
                break
            else:
                retries += 1
                if retries <= MAX_RETRIES:
                    print(f"No data received. Retrying ({retries}/{MAX_RETRIES})...")
                    time.sleep(RATE_LIMIT_SLEEP_SECONDS)

        except requests.RequestsError:
            retries += 1
            if retries <= MAX_RETRIES:
                print(f"Rate limit hit. Waiting {RATE_LIMIT_SLEEP_SECONDS}s before retry {retries}/{MAX_RETRIES}...")
                time.sleep(RATE_LIMIT_SLEEP_SECONDS)
        except Exception as e:
            print(f"Fatal error during scraping: {e}")
            break

    if data and data.get('Results'):
        all_records = data['Results']
        
        # Filter to only include active warrants (FirstTradingDate <= today < LastTradingDate)
        current_date = datetime.now()
        active_records = []
        
        for record in all_records:
            try:
                first_trading_date = datetime.fromisoformat(record['FirstTradingDate'].replace('T00:00:00', ''))
                last_trading_date = datetime.fromisoformat(record['LastTradingDate'].replace('T00:00:00', ''))
                
                # Include if: FirstTradingDate <= current_date < LastTradingDate
                if first_trading_date <= current_date < last_trading_date:
                    active_records.append(record)
            except (ValueError, KeyError) as e:
                print(f"Warning: Skipping record with invalid dates: {e}")
                continue
        
        print(f"Total records fetched: {len(all_records)}")
        print(f"Active warrants (currently tradeable): {len(active_records)}")
        print(f"Filtered out (expired or not yet started): {len(all_records) - len(active_records)}")
        
        combined_data = {
            "totalRecords": len(active_records),
            "filteredDate": current_date.strftime('%Y-%m-%d'),
            "data": active_records
        }
        save_json(OUTPUT_FILE, combined_data)
        print(f"\nData collection complete. Saved {len(active_records)} active warrant records.")

        # Print available fields from the first record
        if active_records:
            print(f"\nAvailable fields per record:")
            for key in active_records[0]:
                print(f"  - {key}: {type(active_records[0][key]).__name__} (e.g. {active_records[0][key]})")
    else:
        print("No data was collected to save.")

if __name__ == "__main__":
    scrape_structured_warrants()
