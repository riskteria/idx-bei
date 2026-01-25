from curl_cffi import requests
import json
import os

# URL for Index Summary
url = "https://www.idx.co.id/primary/TradingSummary/GetIndexSummary?length=9999&start=0"
    
def fetch_index_summary():
    print(f"Fetching {url}...")
    try:
        # Using impersonate="chrome" to bypass Cloudflare
        # No extra headers needed as per previous verification with news endpoint
        response = requests.get(
            url, 
            impersonate="chrome",
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("Successfully parsed JSON.")
                
                # Export to JSON file
                output_file = "index_summary.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                
                print(f"Data saved to {output_file}")
                # Print a snippet to verify
                print(str(data)[:200] + "...")
                return data
            except json.JSONDecodeError:
                print("Failed to decode JSON. Response text snippet:")
                print(response.text[:500])
        else:
            print("Request failed. Response snippet:")
            print(response.text[:500])
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fetch_index_summary()
