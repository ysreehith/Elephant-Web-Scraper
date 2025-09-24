"""
Scrape elephant articles from URLs listed in a text file
Uses the new modular functions from manual_url_scraper.py
"""

import logging
from datetime import datetime
from manual_url_scraper import process_urls_from_file, load_urls
from config import INCLUDE_TIMESTAMP_IN_FILENAME

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """
    Main function to scrape URLs from file using the new modular approach
    """
    print("Elephant News Article Scraper - File-based Processing")
    print("=" * 60)
    
    # Get filename from user
    filename = input("Enter filename containing URLs (e.g., sample_urls.txt): ").strip()
    if not filename:
        filename = "sample_urls.txt"  # Default filename
    
    # Check if file exists
    urls = load_urls(filename)
    if not urls:
        print(f"No URLs found in {filename}. Please check the file and try again.")
        return
    
    print(f"\nFound {len(urls)} URLs in {filename}")
    print("Starting processing...")
    
    # Build output filename
    if INCLUDE_TIMESTAMP_IN_FILENAME:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"elephant_dataset_{timestamp}.csv"
    else:
        output_file = "elephant_dataset.csv"
    
    # Process URLs using the modular function
    process_urls_from_file(filename, output_file)


if __name__ == "__main__":
    main()
