"""
Manual URL Scraper for Elephant News Articles
Processes a list of manually provided article URLs using newspaper3k and Gemini API
"""

import os
import json
import time
import logging
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urlparse

import requests
from newspaper import Article
import google.generativeai as genai

from config import (
    GEMINI_API_KEY, GEMINI_MODEL, GEMINI_MAX_RETRIES, GEMINI_TIMEOUT,
    GEMINI_EXTRACTION_PROMPT, LOG_LEVEL, LOG_FORMAT, START_YEAR, END_YEAR, FILTER_BY_DATE
)

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)

# Configure Gemini API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    # Try to get API key from environment variable
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
    else:
        logger.warning("Gemini API key not found. Please set GEMINI_API_KEY in config.py or as environment variable.")


def load_urls(file_path: str) -> List[str]:
    """
    Load URLs from a text/CSV file (one URL per line)
    
    Args:
        file_path: Path to the file containing URLs
        
    Returns:
        List of URLs
    """
    urls = []
    
    if not os.path.exists(file_path):
        logger.error(f"File {file_path} not found!")
        return urls
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                url = line.strip()
                # Skip empty lines and comments
                if url and not url.startswith('#'):
                    urls.append(url)
        
        logger.info(f"Loaded {len(urls)} URLs from {file_path}")
        
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
    
    return urls


def _is_within_temporal_scope(date_str: str) -> bool:
    """
    Check if article date falls within the specified temporal scope (2000-2025)
    
    Args:
        date_str: Date string to check
        
    Returns:
        True if within scope, False otherwise
    """
    if not FILTER_BY_DATE or not date_str:
        return True
    
    try:
        # Try to extract year from various date formats
        import re
        year_match = re.search(r'(\d{4})', date_str)
        if year_match:
            year = int(year_match.group(1))
            return START_YEAR <= year <= END_YEAR
        
        # If no year found, try to parse the full date
        from datetime import datetime
        try:
            # Try common date formats
            for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y']:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    year = parsed_date.year
                    return START_YEAR <= year <= END_YEAR
                except ValueError:
                    continue
        except (ValueError, AttributeError):
            pass
                
    except (ValueError, IndexError, AttributeError):
        pass
    
    # If we can't determine the year, include the article (better to be inclusive)
    logger.warning(f"Could not determine year for date: {date_str}")
    return True


def fetch_article(url: str) -> Optional[Dict]:
    """
    Fetch article content using newspaper3k
    
    Args:
        url: Article URL to fetch
        
    Returns:
        Dictionary with article data or None if failed
    """
    try:
        logger.info(f"Fetching article: {url}")
        
        # Create Article object
        article = Article(url)
        
        # Download and parse the article
        article.download()
        article.parse()
        
        # Extract domain name for source
        domain = urlparse(url).netloc
        source = domain.replace('www.', '').replace('.com', '').replace('.in', '').title()
        
        # Check if we got valid content
        if not article.title or not article.text:
            logger.warning(f"No content found for: {url}")
            return None
        
        # Format the date
        article_date = article.publish_date.strftime('%Y-%m-%d') if article.publish_date else None
        
        # Check temporal scope (2000-2025)
        if not _is_within_temporal_scope(article_date):
            logger.info(f"Article {url} is outside temporal scope (2000-2025), skipping")
            return None
        
        article_data = {
            'url': url,
            'title': article.title.strip(),
            'date': article_date,
            'source': source,
            'content': article.text.strip()
        }
        
        logger.info(f"Successfully fetched: {article_data['title'][:50]}...")
        return article_data
        
    except Exception as e:
        logger.error(f"Error fetching article {url}: {str(e)}")
        return None


def extract_with_gemini(text: str, url: str, source: str) -> Optional[Dict]:
    """
    Extract structured data using Gemini API
    
    Args:
        text: Article text content
        url: Article URL
        source: Source domain name
        
    Returns:
        Dictionary with extracted structured data or None if failed
    """
    try:
        # Check if Gemini is configured
        api_key = GEMINI_API_KEY or os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.error("Gemini API not configured. Please set GEMINI_API_KEY.")
            return None
        
        # Prepare the prompt
        prompt = GEMINI_EXTRACTION_PROMPT.format(
            article_text=text,
            url=url,
            source=source
        )
        
        # Initialize the model
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Retry logic
        for attempt in range(GEMINI_MAX_RETRIES):
            try:
                logger.info(f"Extracting data with Gemini (attempt {attempt + 1}/{GEMINI_MAX_RETRIES})")
                
                # Generate content
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,  # Low temperature for consistent extraction
                        max_output_tokens=1000,
                    )
                )
                
                # Extract JSON from response
                response_text = response.text.strip()
                
                # Try to find JSON in the response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_text = response_text[json_start:json_end]
                    extracted_data = json.loads(json_text)
                    
                    # Validate required fields
                    required_fields = [
                        'Date', 'State', 'District', 'Block', 'Village',
                        'No. of Elephants', 'Type of Incident', 'Human Deaths',
                        'Elephant Deaths', 'Damage (Crop/Property/Other)',
                        'Source', 'URL'
                    ]
                    
                    # Ensure all required fields are present
                    for field in required_fields:
                        if field not in extracted_data:
                            extracted_data[field] = None
                    
                    logger.info("Successfully extracted structured data with Gemini")
                    return extracted_data
                else:
                    logger.warning(f"No valid JSON found in Gemini response: {response_text[:200]}...")
                    
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode error (attempt {attempt + 1}): {str(e)}")
                if attempt < GEMINI_MAX_RETRIES - 1:
                    time.sleep(2)  # Wait before retry
                    continue
                else:
                    logger.error("Failed to parse JSON after all retries")
                    return None
                    
            except Exception as e:
                logger.warning(f"Gemini API error (attempt {attempt + 1}): {str(e)}")
                if attempt < GEMINI_MAX_RETRIES - 1:
                    time.sleep(2)  # Wait before retry
                    continue
                else:
                    logger.error("Failed to extract data with Gemini after all retries")
                    return None
        
        return None
        
    except Exception as e:
        logger.error(f"Error in extract_with_gemini: {str(e)}")
        return None


def save_to_csv(data: List[Dict], filename: str = "elephant_dataset.csv") -> None:
    """
    Save extracted data to CSV file
    
    Args:
        data: List of dictionaries containing extracted data
        filename: Output CSV filename
    """
    try:
        if not data:
            logger.warning("No data to save")
            return
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Save to CSV
        df.to_csv(filename, index=False, encoding='utf-8')
        logger.info(f"Data saved to {filename}")
        
        # Display summary statistics
        print(f"\n{'='*60}")
        print(f"DATA EXTRACTION COMPLETED")
        print(f"{'='*60}")
        print(f"Total records: {len(df)}")
        print(f"Data saved to: {filename}")
        
        if len(df) > 0:
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
        
        # Display sample data
        print(f"\nSample Data:")
        print(df.head().to_string())
        
    except Exception as e:
        logger.error(f"Error saving data to CSV: {str(e)}")


def process_urls_from_file(file_path: str, output_filename: str = "elephant_dataset.csv") -> None:
    """
    Main function to process URLs from file and extract structured data
    
    Args:
        file_path: Path to file containing URLs
        output_filename: Output CSV filename
    """
    # Load URLs
    urls = load_urls(file_path)
    
    if not urls:
        logger.error("No URLs found in file")
        return
    
    logger.info(f"Processing {len(urls)} URLs...")
    
    # Process each URL
    extracted_data = []
    successful_fetches = 0
    successful_extractions = 0
    
    for i, url in enumerate(urls, 1):
        logger.info(f"Processing URL {i}/{len(urls)}: {url}")
        
        # Fetch article
        article_data = fetch_article(url)
        if not article_data:
            logger.warning(f"Failed to fetch article: {url}")
            continue
        
        successful_fetches += 1
        
        # Extract structured data with Gemini
        structured_data = extract_with_gemini(
            article_data['content'],
            article_data['url'],
            article_data['source']
        )
        
        if structured_data:
            # Update with article metadata
            structured_data['Source'] = article_data['source']
            structured_data['URL'] = article_data['url']
            if article_data['date']:
                structured_data['Date'] = article_data['date']
            
            extracted_data.append(structured_data)
            successful_extractions += 1
            logger.info(f"Successfully processed: {article_data['title'][:50]}...")
        else:
            logger.warning(f"Failed to extract structured data for: {url}")
        
        # Add delay between requests to be respectful
        time.sleep(2)
    
    # Save results
    logger.info(f"Processing complete. Fetched: {successful_fetches}, Extracted: {successful_extractions}")
    save_to_csv(extracted_data, output_filename)


def main():
    """
    Main function for interactive use
    """
    print("Elephant News Article Scraper")
    print("=" * 50)
    
    # Check if Gemini API is configured
    api_key = GEMINI_API_KEY or os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("ERROR: Gemini API key not configured!")
        print("Please set GEMINI_API_KEY in config.py or as environment variable.")
        return
    
    # Get input file
    file_path = input("Enter path to file containing URLs (e.g., sample_urls.txt): ").strip()
    if not file_path:
        file_path = "sample_urls.txt"
    
    # Get output filename
    output_filename = input("Enter output CSV filename (default: elephant_dataset.csv): ").strip()
    if not output_filename:
        output_filename = "elephant_dataset.csv"
    
    # Process URLs
    process_urls_from_file(file_path, output_filename)


if __name__ == "__main__":
    main()
