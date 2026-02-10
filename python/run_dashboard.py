#!/usr/bin/env python3
"""
Wrapper script to:
1. Scrape structured warrants and underlying data
2. Serve the HTML dashboard
"""

import os
import sys
import subprocess
import http.server
import socketserver
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / 'data'
PORT = 8090

def get_python_executable():
    """Get the Python executable, preferring venv if available."""
    venv_python = PROJECT_ROOT / '.venv' / 'bin' / 'python'
    if venv_python.exists():
        return str(venv_python)
    return sys.executable

def run_scraper():
    """Run the structured warrant + underlying scraper pipeline."""
    print("=" * 70)
    print("Starting data collection...")
    print("=" * 70)
    
    scraper_script = SCRIPT_DIR / 'scrape_sw_combined.py'
    python_exe = get_python_executable()
    
    try:
        result = subprocess.run(
            [python_exe, str(scraper_script)],
            cwd=str(PROJECT_ROOT),
            check=True,
            text=True
        )
        print("\n" + "=" * 70)
        print("Data collection completed successfully!")
        print("=" * 70)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nError running scraper: {e}")
        return False

def serve_dashboard():
    """Serve the HTML dashboard on localhost."""
    os.chdir(DATA_DIR)
    
    Handler = http.server.SimpleHTTPRequestHandler
    
    print("\n" + "=" * 70)
    print(f"Starting dashboard server...")
    print(f"Dashboard URL: http://localhost:{PORT}/structured_warrants.html")
    print("Press Ctrl+C to stop the server")
    print("=" * 70)
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"\nError: Port {PORT} is already in use.")
            print(f"Try opening: http://localhost:{PORT}/structured_warrants.html")
        else:
            print(f"\nError starting server: {e}")

def main():
    """Main execution."""
    print("\n" + "=" * 70)
    print("IDX Structured Warrants Dashboard Runner")
    print("=" * 70)
    
    # Check if data directory exists
    if not DATA_DIR.exists():
        print(f"Error: Data directory not found: {DATA_DIR}")
        sys.exit(1)
    
    # Ask user if they want to refresh data
    print("\nOptions:")
    print("  1. Refresh data and serve dashboard (recommended)")
    print("  2. Serve dashboard with existing data")
    print("  3. Refresh data only (no server)")
    
    try:
        choice = input("\nChoice [1]: ").strip() or "1"
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.")
        sys.exit(0)
    
    if choice == "1":
        # Refresh data then serve
        if run_scraper():
            serve_dashboard()
        else:
            print("\nFailed to refresh data. Exiting.")
            sys.exit(1)
    
    elif choice == "2":
        # Just serve existing data
        combined_file = DATA_DIR / 'structured_warrants_combined.json'
        if not combined_file.exists():
            print(f"\nWarning: {combined_file.name} not found!")
            print("You may need to run the scraper first (option 1 or 3).")
            try:
                proceed = input("Serve anyway? [y/N]: ").strip().lower()
                if proceed != 'y':
                    sys.exit(0)
            except (KeyboardInterrupt, EOFError):
                print("\nCancelled.")
                sys.exit(0)
        serve_dashboard()
    
    elif choice == "3":
        # Refresh data only
        if run_scraper():
            print("\nData refreshed successfully!")
            print(f"To view the dashboard, run: python {__file__} (and choose option 2)")
        else:
            print("\nFailed to refresh data.")
            sys.exit(1)
    
    else:
        print(f"\nInvalid choice: {choice}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Exiting.")
        sys.exit(0)
