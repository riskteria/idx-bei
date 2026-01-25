from curl_cffi import requests
import json

# URL and Headers
url = "https://www.idx.co.id/primary/home/content"
headers = {
    "accept": "application/json, text/plain, */*",
    "Referer": "https://www.idx.co.id/id/berita/berita/"
}

def fetch_news():
    print(f"Fetching {url}...")
    try:
        # impersonate="chrome" is usually sufficient to bypass basic Cloudflare checks
        response = requests.get(
            url, 
            headers=headers, 
            impersonate="chrome",
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("Successfully parsed JSON.")
                # Print a snippet to verify content
                print(json.dumps(data, indent=2)[:500] + "...")
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
    fetch_news()
