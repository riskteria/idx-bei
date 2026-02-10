import os
import time
import json
import sys
from datetime import datetime
import yfinance as yf

# --- Configuration ---
YAHOO_SUFFIX = ".JK"  # Jakarta Stock Exchange suffix for Yahoo Finance

# File Paths (relative to the python/ directory)
DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')
OUTPUT_FILE = os.path.join(DATA_DIR, 'underlying_ohlc.json')

# Rate limiting
REQUEST_DELAY_SECONDS = 0.3
MAX_RETRIES = 3

# --- Utility Functions ---

def ensure_data_dir():
    """Ensures the data directory exists."""
    os.makedirs(DATA_DIR, exist_ok=True)

def save_json(file_path, data):
    """Saves data to a JSON file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Successfully saved data to {os.path.basename(file_path)}")
    except IOError as e:
        print(f"Error saving data to {file_path}: {e}")

def fetch_ohlc(ticker_code):
    """Fetches the latest OHLC data for a single IDX ticker from Yahoo Finance.

    Args:
        ticker_code: IDX ticker code (e.g. 'BBCA', 'TLKM')

    Returns:
        dict with OHLC data or None on failure
    """
    yf_ticker = f"{ticker_code}{YAHOO_SUFFIX}"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            stock = yf.Ticker(yf_ticker)
            hist = stock.history(period="5d")

            if hist.empty:
                print(f"  Warning: No data returned for {yf_ticker}")
                return None

            # Get the latest trading day
            latest = hist.iloc[-1]
            trade_date = hist.index[-1]

            return {
                "ticker": ticker_code,
                "yahooTicker": yf_ticker,
                "date": trade_date.strftime('%Y-%m-%d'),
                "open": round(float(latest['Open']), 2),
                "high": round(float(latest['High']), 2),
                "low": round(float(latest['Low']), 2),
                "close": round(float(latest['Close']), 2),
                "volume": int(latest['Volume']),
            }

        except Exception as e:
            if attempt < MAX_RETRIES:
                print(f"  Attempt {attempt}/{MAX_RETRIES} failed for {yf_ticker}: {e}. Retrying...")
                time.sleep(2)
            else:
                print(f"  Error fetching {yf_ticker} after {MAX_RETRIES} attempts: {e}")
                return None

    return None

# --- Main Scraper ---

def scrape_underlying_ohlc(ticker_codes):
    """Fetches latest OHLC for a list of IDX ticker codes from Yahoo Finance.

    Args:
        ticker_codes: list of IDX ticker codes (e.g. ['BBCA', 'TLKM', ...])

    Returns:
        dict mapping ticker_code -> OHLC data
    """
    ensure_data_dir()

    print(f"Fetching OHLC data for {len(ticker_codes)} underlying tickers from Yahoo Finance...")

    ohlc_map = {}
    success_count = 0
    fail_count = 0

    for i, code in enumerate(ticker_codes, 1):
        print(f"[{i}/{len(ticker_codes)}] Fetching {code}{YAHOO_SUFFIX}...")
        ohlc = fetch_ohlc(code)

        if ohlc:
            ohlc_map[code] = ohlc
            success_count += 1
        else:
            fail_count += 1

        time.sleep(REQUEST_DELAY_SECONDS)

    result = {
        "fetchedAt": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "totalTickers": len(ticker_codes),
        "successCount": success_count,
        "failCount": fail_count,
        "data": ohlc_map
    }

    save_json(OUTPUT_FILE, result)
    print(f"\nOHLC collection complete. Success: {success_count}, Failed: {fail_count}")

    return result

if __name__ == "__main__":
    # Standalone mode: read unique underlyings from structured_warrants.json
    sw_file = os.path.join(DATA_DIR, 'structured_warrants.json')

    if not os.path.exists(sw_file):
        print(f"Error: {sw_file} not found. Run scrape_structured_warrants.py first.")
        sys.exit(1)

    with open(sw_file, 'r', encoding='utf-8') as f:
        sw_data = json.load(f)

    tickers = sorted(set(record['Underlying'] for record in sw_data['data']))
    print(f"Found {len(tickers)} unique underlying tickers from structured warrants data.")

    scrape_underlying_ohlc(tickers)
