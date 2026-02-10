import os
import json
import sys
from datetime import datetime

# Import the individual scrapers
from scrape_structured_warrants import scrape_structured_warrants
from scrape_underlying_ohlc import scrape_underlying_ohlc
from scrape_warrant_prices import scrape_warrant_prices

# --- Configuration ---
DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')
SW_FILE = os.path.join(DATA_DIR, 'structured_warrants.json')
OHLC_FILE = os.path.join(DATA_DIR, 'underlying_ohlc.json')
PRICES_FILE = os.path.join(DATA_DIR, 'warrant_prices.json')
COMBINED_FILE = os.path.join(DATA_DIR, 'structured_warrants_combined.json')

def save_json(file_path, data):
    """Saves data to a JSON file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Successfully saved data to {os.path.basename(file_path)}")
    except IOError as e:
        print(f"Error saving data to {file_path}: {e}")

def parse_exercise_ratio(ratio_str):
    """Parse exercise ratio string (e.g., '3.0:1.0') to get conversion factor.
    
    Returns the number of warrants needed to exercise for 1 share.
    E.g., '3.0:1.0' means 3 warrants = 1 share, so ratio is 3.0
    """
    try:
        parts = ratio_str.split(':')
        if len(parts) == 2:
            return float(parts[0]) / float(parts[1])
    except:
        pass
    return None

def calculate_warrant_metrics(record, underlying_price):
    """Calculate potential gain/loss and other metrics for a warrant.
    
    Args:
        record: warrant record with ExercisePrice, ExerciseRatio, SWType
        underlying_price: current market price of underlying stock
    
    Returns:
        dict with calculated metrics
    """
    exercise_price = record.get('ExercisePrice')
    exercise_ratio_str = record.get('ExerciseRatio', '')
    sw_type = record.get('SWType', '').lower()
    
    if not exercise_price or not underlying_price:
        return None
    
    exercise_ratio = parse_exercise_ratio(exercise_ratio_str)
    if not exercise_ratio:
        return None
    
    # Calculate intrinsic value per warrant
    if sw_type == 'call':
        # Call: right to buy at exercise price
        # Intrinsic value = (Underlying Price - Exercise Price) / Exercise Ratio
        intrinsic_value = (underlying_price - exercise_price) / exercise_ratio
        is_itm = underlying_price > exercise_price  # In the money
        
    elif sw_type == 'put':
        # Put: right to sell at exercise price
        # Intrinsic value = (Exercise Price - Underlying Price) / Exercise Ratio
        intrinsic_value = (exercise_price - underlying_price) / exercise_ratio
        is_itm = exercise_price > underlying_price  # In the money
    else:
        return None
    
    # Calculate moneyness percentage
    # How far in/out of the money (as % of exercise price)
    moneyness_pct = ((underlying_price - exercise_price) / exercise_price) * 100
    
    # Intrinsic value can't be negative (warrant can expire worthless but not negative value)
    intrinsic_value_adjusted = max(0, intrinsic_value)
    
    return {
        "intrinsicValue": round(intrinsic_value, 2),
        "intrinsicValueAdjusted": round(intrinsic_value_adjusted, 2),
        "moneynessPercent": round(moneyness_pct, 2),
        "isInTheMoney": is_itm,
        "exerciseRatioNumeric": round(exercise_ratio, 4),
    }

def combine_data():
    """Combines structured warrants data with underlying OHLC prices and warrant prices.

    Reads JSON files and enriches each warrant record with:
    - Latest OHLC data of underlying stock
    - Warrant price/trading data (OHLC, volume, bid/offer)
    - Calculated gain/loss metrics
    """
    # Load structured warrants
    if not os.path.exists(SW_FILE):
        print(f"Error: {SW_FILE} not found.")
        return None
    with open(SW_FILE, 'r', encoding='utf-8') as f:
        sw_data = json.load(f)

    # Load OHLC data
    if not os.path.exists(OHLC_FILE):
        print(f"Error: {OHLC_FILE} not found.")
        return None
    with open(OHLC_FILE, 'r', encoding='utf-8') as f:
        ohlc_data = json.load(f)

    # Load warrant prices
    warrant_prices_map = {}
    if os.path.exists(PRICES_FILE):
        with open(PRICES_FILE, 'r', encoding='utf-8') as f:
            prices_data = json.load(f)
            warrant_prices_map = prices_data.get('data', {})
        print(f"Loaded {len(warrant_prices_map)} warrant prices")
    else:
        print(f"Warning: {PRICES_FILE} not found. Skipping warrant prices.")
        prices_data = None

    ohlc_map = ohlc_data.get('data', {})

    # Enrich each warrant record with underlying OHLC, warrant prices, and calculations
    combined_records = []
    matched_ohlc = 0
    unmatched_ohlc = 0
    matched_prices = 0

    for record in sw_data.get('data', []):
        underlying = record['Underlying']
        kod_sw = record['KodeSW']
        ohlc = ohlc_map.get(underlying)
        warrant_price = warrant_prices_map.get(kod_sw)

        enriched = {**record}
        
        # Add underlying OHLC
        if ohlc:
            enriched['UnderlyingOHLC'] = {
                "date": ohlc['date'],
                "open": ohlc['open'],
                "high": ohlc['high'],
                "low": ohlc['low'],
                "close": ohlc['close'],
                "volume": ohlc['volume'],
            }
            
            # Calculate warrant metrics based on closing price
            metrics = calculate_warrant_metrics(record, ohlc['close'])
            if metrics:
                enriched['WarrantMetrics'] = metrics
            else:
                enriched['WarrantMetrics'] = None
            
            matched_ohlc += 1
        else:
            enriched['UnderlyingOHLC'] = None
            enriched['WarrantMetrics'] = None
            unmatched_ohlc += 1

        # Add warrant price data
        if warrant_price:
            enriched['WarrantPrice'] = {
                "open": warrant_price['open'],
                "high": warrant_price['high'],
                "low": warrant_price['low'],
                "last": warrant_price['last'],
                "change": warrant_price['change'],
                "percentChange": warrant_price['percentChange'],
                "bid": warrant_price['bid'],
                "offer": warrant_price['offer'],
                "volume": warrant_price['volume'],
                "value": warrant_price['value'],
                "tradeDate": warrant_price['tradeDate']
            }
            matched_prices += 1
        else:
            enriched['WarrantPrice'] = None

        combined_records.append(enriched)

    # Calculate statistics
    itm_count = sum(1 for r in combined_records 
                    if r.get('WarrantMetrics') and r['WarrantMetrics']['isInTheMoney'])
    otm_count = sum(1 for r in combined_records 
                    if r.get('WarrantMetrics') and not r['WarrantMetrics']['isInTheMoney'])
    call_count = sum(1 for r in combined_records if r.get('SWType', '').lower() == 'call')
    put_count = sum(1 for r in combined_records if r.get('SWType', '').lower() == 'put')
    
    # Warrant price statistics
    with_volume = sum(1 for r in combined_records 
                     if r.get('WarrantPrice') and r['WarrantPrice']['volume'] > 0)
    with_trades = sum(1 for r in combined_records 
                     if r.get('WarrantPrice') and r['WarrantPrice']['last'] > 0)

    combined = {
        "generatedAt": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "warrantFilteredDate": sw_data.get('filteredDate'),
        "ohlcFetchedAt": ohlc_data.get('fetchedAt'),
        "pricesFetchedAt": prices_data.get('fetchedAt') if prices_data else None,
        "totalWarrants": len(combined_records),
        "withOHLC": matched_ohlc,
        "withoutOHLC": unmatched_ohlc,
        "withPrices": matched_prices,
        "statistics": {
            "callWarrants": call_count,
            "putWarrants": put_count,
            "inTheMoney": itm_count,
            "outOfTheMoney": otm_count,
            "withVolume": with_volume,
            "withTrades": with_trades
        },
        "data": combined_records
    }

    save_json(COMBINED_FILE, combined)
    print(f"\nCombined data:")
    print(f"  - {matched_ohlc} warrants with underlying OHLC")
    print(f"  - {matched_prices} warrants with price data")
    print(f"  - Statistics: {call_count} calls, {put_count} puts")
    print(f"  - Moneyness: {itm_count} ITM, {otm_count} OTM")
    print(f"  - Trading: {with_trades} with prices, {with_volume} with volume")

    return combined

def main():
    """Orchestrator: runs the full pipeline.

    1. Scrape active structured warrants from IDX
    2. Extract unique underlying tickers
    3. Fetch latest OHLC from Yahoo Finance for underlyings
    4. Fetch warrant prices from IDX
    5. Combine everything into a single JSON
    """
    print("=" * 60)
    print("  Structured Warrant Analysis Pipeline")
    print("=" * 60)

    # Step 1: Scrape structured warrants
    print("\n--- Step 1/4: Scraping structured warrants from IDX ---")
    scrape_structured_warrants()

    # Load the result to extract unique underlyings
    if not os.path.exists(SW_FILE):
        print("Error: Structured warrants scrape failed. Aborting.")
        sys.exit(1)

    with open(SW_FILE, 'r', encoding='utf-8') as f:
        sw_data = json.load(f)

    tickers = sorted(set(record['Underlying'] for record in sw_data['data']))
    print(f"\nFound {len(tickers)} unique underlying tickers.")

    # Step 2: Fetch OHLC data from Yahoo Finance
    print("\n--- Step 2/4: Fetching underlying OHLC from Yahoo Finance ---")
    scrape_underlying_ohlc(tickers)

    # Step 3: Fetch warrant prices from IDX
    print("\n--- Step 3/4: Fetching warrant prices from IDX ---")
    result = scrape_warrant_prices()
    if result:
        # Save warrant prices
        save_json(PRICES_FILE, result)
    else:
        print("Warning: Warrant price scraping failed. Continuing without prices.")

    # Step 4: Combine data
    print("\n--- Step 4/4: Combining warrants + OHLC + prices ---")
    combine_data()

    print("\n" + "=" * 60)
    print("  Pipeline complete!")
    print(f"  Output: data/structured_warrants_combined.json")
    print("=" * 60)

if __name__ == "__main__":
    main()
