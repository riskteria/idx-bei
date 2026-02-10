#!/usr/bin/env python3
"""
Scrape structured warrant trading/price data from IDX.
Returns OHLC, volume, bid/offer for all structured warrants.
"""

import os
import json
from datetime import datetime
from curl_cffi import requests


# Constants
BASE_URL = "https://www.idx.co.id"
TRADING_ENDPOINT = f"{BASE_URL}/secondary/get/StructuredWarrant/Trading"
MAX_RETRIES = 3


def fetch_data(url, params=None):
    """Fetch data from IDX API with retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(
                url,
                params=params,
                impersonate="chrome",
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:  # Rate limit
                print(f"Rate limited, retrying ({attempt + 1}/{MAX_RETRIES})...")
                continue
            elif response.status_code == 503:  # Service unavailable
                print(f"Service unavailable, retrying ({attempt + 1}/{MAX_RETRIES})...")
                continue
            else:
                print(f"Error: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Request failed ({attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt == MAX_RETRIES - 1:
                return None
    
    return None


def scrape_warrant_prices():
    """
    Scrape warrant trading/price data from IDX.
    
    Returns:
        dict: {
            'fetchedAt': ISO timestamp,
            'totalWarrants': int,
            'data': {
                'KodeSW': {
                    'kodeSW': str,
                    'kodeEmiten': str,
                    'open': float,
                    'high': float,
                    'low': float,
                    'last': float (closing price),
                    'change': float,
                    'percentChange': float,
                    'bid': float,
                    'offer': float (ask),
                    'volume': float,
                    'value': float,
                    'tradeDate': str (ISO format)
                }
            }
        }
    """
    print(f"Fetching warrant trading data from: {TRADING_ENDPOINT}")
    
    # Fetch all warrant trading data
    params = {
        'start': 0,
        'length': 9999  # Get all records
    }
    
    data = fetch_data(TRADING_ENDPOINT, params)
    
    if not data:
        print("Failed to fetch warrant trading data")
        return None
    
    # Parse response
    warrants = data['Results']
    print(f"Fetched {len(warrants)} warrant trading records")
    
    # Transform to dictionary keyed by KodeSW
    warrant_prices = {}
    
    for w in warrants:
        kod_sw = w['KodeSW']
        warrant_prices[kod_sw] = {
            'kodeSW': kod_sw,
            'kodeEmiten': w['KodeEmiten'],
            'open': w['Open'],
            'high': w['High'],
            'low': w['Low'],
            'last': w['Last'],
            'change': w['Change'],
            'percentChange': w['PercentChange'],
            'bid': w['Bid'],
            'offer': w['Offer'],
            'volume': w['Volume'],
            'value': w['Value'],
            'tradeDate': w['TradeDate']
        }
    
    # Count active warrants (with recent trades or non-zero volume)
    active_count = sum(1 for w in warrant_prices.values() 
                      if w['volume'] > 0 or w['last'] > 0)
    
    result = {
        'fetchedAt': datetime.now().isoformat(),
        'totalWarrants': len(warrant_prices),
        'activeWarrants': active_count,
        'data': warrant_prices
    }
    
    print(f"Active warrants (with prices): {active_count}")
    
    return result


def ensure_data_dir():
    """Ensure the data directory exists."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(script_dir), 'data')
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def save_json(data, filename):
    """Save data to JSON file."""
    data_dir = ensure_data_dir()
    filepath = os.path.join(data_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved to: {filepath}")
    return filepath


def main():
    """Main execution function."""
    print("="*70)
    print("Scraping Structured Warrant Prices from IDX")
    print("="*70)
    
    # Scrape warrant prices
    result = scrape_warrant_prices()
    
    if result:
        # Save to file
        save_json(result, 'warrant_prices.json')
        
        print("\n" + "="*70)
        print("Summary:")
        print(f"  Total warrants: {result['totalWarrants']}")
        print(f"  Active warrants: {result['activeWarrants']}")
        print(f"  Fetched at: {result['fetchedAt']}")
        print("="*70)
    else:
        print("Failed to scrape warrant prices")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
