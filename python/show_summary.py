#!/usr/bin/env python3
"""Display summary of the structured warrant analysis system"""

import json
import os

data_dir = os.path.join(os.path.dirname(__file__), '../data')
combined_file = os.path.join(data_dir, 'structured_warrants_combined.json')

with open(combined_file, 'r') as f:
    data = json.load(f)

print('='*70)
print('STRUCTURED WARRANT ANALYSIS SYSTEM - FINAL STATUS')
print('='*70)
print(f'Generated: {data["generatedAt"]}')
print(f'Total Active Warrants: {data["totalWarrants"]}')
print()
print('DATA COVERAGE:')
print(f'  ✓ Warrant Info: {data["totalWarrants"]}')
print(f'  ✓ Underlying OHLC: {data["withOHLC"]}')
print(f'  ✓ Warrant Prices: {data["withPrices"]}')
print()
print('STATISTICS:')
print(f'  Call Warrants: {data["statistics"]["callWarrants"]}')
print(f'  Put Warrants: {data["statistics"]["putWarrants"]}')
print(f'  In the Money: {data["statistics"]["inTheMoney"]}')
print(f'  Out of the Money: {data["statistics"]["outOfTheMoney"]}')
print(f'  With Trading Volume: {data["statistics"]["withVolume"]}')
print()
print('SAMPLE WARRANT (with full data):')
for w in data['data']:
    if w.get('WarrantPrice') and w['WarrantPrice']['volume'] > 0:
        print(f'  Code: {w["KodeSW"]}')
        print(f'  Type: {w["SWType"]}')
        print(f'  Underlying: {w["Underlying"]} @ {w["UnderlyingOHLC"]["close"]}')
        print(f'  Warrant Price: {w["WarrantPrice"]["last"]} (Volume: {w["WarrantPrice"]["volume"]:,.0f})')
        print(f'  Intrinsic Value: {w["WarrantMetrics"]["intrinsicValue"]} ({"ITM" if w["WarrantMetrics"]["isInTheMoney"] else "OTM"})')
        print(f'  Days to Expiry: {w["TimetoLastTradingDate"]}')
        break
print('='*70)
print()
print('FILES GENERATED:')
print('  • data/structured_warrants.json - Active warrants from IDX')
print('  • data/underlying_ohlc.json - Stock prices from Yahoo Finance')
print('  • data/warrant_prices.json - Warrant trading data from IDX')
print('  • data/structured_warrants_combined.json - Complete dataset')
print('  • data/structured_warrants.html - Interactive dashboard')
print()
print('DASHBOARD:')
print('  → http://localhost:8090/structured_warrants.html')
print('='*70)
