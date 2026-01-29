from curl_cffi import requests
import json
import os
import time

# Base URL for IDX API
BASE_URL = "https://www.idx.co.id/primary"

def get_company_profiles():
    """Get all company profiles"""
    url = f"{BASE_URL}/ListedCompany/GetCompanyProfiles?start=0&length=9999"
    headers = {
        "accept": "application/json, text/plain, */*",
        "referer": "https://www.idx.co.id/"
    }

    print(f"Fetching company profiles from {url}...")
    try:
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
                print(f"Successfully fetched {len(data.get('data', []))} companies")
                return data
            except json.JSONDecodeError:
                print("Failed to decode JSON. Response text snippet:")
                print(response.text[:500])
                return None
        else:
            print("Request failed. Response snippet:")
            print(response.text[:500])
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_company_detail(kode_emiten):
    """Get detailed information for a specific company"""
    url = f"{BASE_URL}/ListedCompany/GetCompanyProfilesDetail?KodeEmiten={kode_emiten}&language=id-id"
    headers = {
        "accept": "application/json, text/plain, */*",
        "referer": "https://www.idx.co.id/"
    }

    print(f"Fetching details for {kode_emiten}...")
    try:
        response = requests.get(
            url,
            headers=headers,
            impersonate="chrome",
            timeout=30
        )

        if response.status_code == 200:
            try:
                data = response.json()
                return data
            except json.JSONDecodeError:
                print(f"Failed to decode JSON for {kode_emiten}")
                return None
        else:
            print(f"Request failed for {kode_emiten}: {response.status_code}")
            return None

    except Exception as e:
        print(f"Error fetching details for {kode_emiten}: {e}")
        return None

def save_incrementally(data, filename):
    """Save data incrementally to preserve existing data"""
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    else:
        existing_data = {}

    # Merge new data with existing
    existing_data.update(data)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(data)} new company details to {filename}")

def main():
    # Load existing companies if file exists
    companies_file = "../data/allCompanies.json"
    details_file = "../data/companyDetailsByKodeEmiten.json"

    if not os.path.exists(companies_file):
        print("Fetching all company profiles first...")
        companies_data = get_company_profiles()
        if companies_data:
            with open(companies_file, 'w', encoding='utf-8') as f:
                json.dump(companies_data, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(companies_data.get('data', []))} companies to {companies_file}")
        else:
            print("Failed to fetch company profiles")
            return
    else:
        with open(companies_file, 'r', encoding='utf-8') as f:
            companies_data = json.load(f)

    # Load existing details
    if os.path.exists(details_file):
        with open(details_file, 'r', encoding='utf-8') as f:
            existing_details = json.load(f)
        print(f"Loaded {len(existing_details)} existing company details")
    else:
        existing_details = {}

    # Process companies
    companies = companies_data.get('data', [])
    new_details = {}
    processed_count = 0

    for company in companies:
        kode_emiten = company.get('KodeEmiten')

        if not kode_emiten:
            continue

        # Skip if already processed
        if kode_emiten in existing_details:
            print(f"Skipping already processed {kode_emiten}")
            continue

        # Fetch company details
        detail = get_company_detail(kode_emiten)
        if detail:
            new_details[kode_emiten] = detail
            processed_count += 1

            # Save incrementially every 5 companies or at the end
            if processed_count % 5 == 0 or processed_count == len(companies):
                save_incrementally(new_details, details_file)
                new_details = {}  # Clear after saving

        # Rate limiting - wait between requests
        time.sleep(1)  # 1 second between requests

    # Save any remaining details
    if new_details:
        save_incrementally(new_details, details_file)

    print(f"\nCompleted! Processed {processed_count} new company details")

if __name__ == "__main__":
    main()