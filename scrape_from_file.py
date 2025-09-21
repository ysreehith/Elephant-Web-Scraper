"""
Scrape elephant articles from URLs listed in a text file
"""

import os
from manual_url_scraper import ManualURLScraper, ElephantDataExtractor
import pandas as pd
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_urls_from_file(filename: str) -> list:
    """
    Load URLs from a text file (one URL per line)
    """
    urls = []
    
    if not os.path.exists(filename):
        logger.error(f"File {filename} not found!")
        return urls
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                if url and not url.startswith('#'):  # Skip empty lines and comments
                    urls.append(url)
        
        logger.info(f"Loaded {len(urls)} URLs from {filename}")
        
    except Exception as e:
        logger.error(f"Error reading file {filename}: {str(e)}")
    
    return urls

def main():
    """
    Main function to scrape URLs from file
    """
    # Initialize scraper and extractor
    scraper = ManualURLScraper()
    extractor = ElephantDataExtractor(scraper.nlp)
    
    # Get filename from user
    filename = input("Enter filename containing URLs (e.g., urls.txt): ").strip()
    
    if not filename:
        filename = "urls.txt"  # Default filename
    
    # Load URLs from file
    urls = load_urls_from_file(filename)
    
    if not urls:
        print("No URLs found in file. Please check the file and try again.")
        return
    
    print(f"\nProcessing {len(urls)} URLs from {filename}...")
    
    # Scrape articles
    articles = scraper.scrape_urls(urls)
    
    if not articles:
        logger.warning("No articles were successfully scraped!")
        return
    
    # Extract structured data
    structured_data = []
    for article in articles:
        try:
            structured_article = extractor.extract_structured_data(article)
            structured_data.append(structured_article)
        except Exception as e:
            logger.error(f"Error processing article: {str(e)}")
            continue
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(structured_data)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"file_elephant_data_{timestamp}.csv"
    
    df.to_csv(output_filename, index=False, encoding='utf-8')
    logger.info(f"Data saved to {output_filename}")
    
    # Display summary
    print(f"\n{'='*60}")
    print(f"FILE-BASED SCRAPING COMPLETED")
    print(f"{'='*60}")
    print(f"URLs processed: {len(urls)}")
    print(f"Articles scraped: {len(articles)}")
    print(f"Articles processed: {len(structured_data)}")
    print(f"Data saved to: {output_filename}")
    
    # Display sample data
    if len(df) > 0:
        print(f"\nSample Data:")
        print(df.head().to_string())
        
        # Display statistics
        print(f"\nData Statistics:")
        print(f"Articles with location data: {df['State'].notna().sum()}")
        print(f"Articles with elephant count: {df['No. of Elephants'].notna().sum()}")
        print(f"Articles with incident type: {df['Type of Incident'].notna().sum()}")
        print(f"Articles with human deaths: {df['Human Deaths'].notna().sum()}")
        print(f"Articles with elephant deaths: {df['Elephant Deaths'].notna().sum()}")
        print(f"Articles with damage info: {df['Damage (Crop/Property/Other)'].notna().sum()}")
        
        # State-wise distribution
        if df['State'].notna().sum() > 0:
            print(f"\nState-wise Distribution:")
            state_counts = df['State'].value_counts()
            for state, count in state_counts.items():
                print(f"{state}: {count} articles")

if __name__ == "__main__":
    main()
