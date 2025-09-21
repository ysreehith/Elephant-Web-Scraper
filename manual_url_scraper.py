"""
Manual URL Scraper for Elephant News Articles
Processes a list of manually provided article URLs
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import spacy
import re
import time
import logging
from urllib.parse import urljoin, urlparse
from datetime import datetime
from typing import List, Dict, Optional
import os
from config import CENTRAL_INDIA_STATES, CENTRAL_INDIA_DISTRICTS, EXTRACTION_PATTERNS, START_YEAR, END_YEAR, FILTER_BY_DATE, DATE_PATTERNS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ManualURLScraper:
    """
    Scraper for manually provided article URLs
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.error("spaCy model 'en_core_web_sm' not found. Please install it with: python -m spacy download en_core_web_sm")
            raise
        
        # Website-specific configurations
        self.site_configs = {
            'thehindu.com': {
                'title_selectors': ['h1.title', 'h1.heading', '.article-title h1', 'h1'],
                'date_selectors': ['.publish-time', '.date', '.article-date', '.published-on'],
                'content_selectors': ['.article-content p', '.story-content p', '.article-body p', 'article p'],
                'source_name': 'The Hindu'
            },
            'timesofindia.indiatimes.com': {
                'title_selectors': ['h1._1Y-96', 'h1.heading', 'h1', '.article-title'],
                'date_selectors': ['._3Mkg-', '.date', '.article-date', '.published-on'],
                'content_selectors': ['._3YYSt p', '.article-content p', '.story-content p', 'article p'],
                'source_name': 'Times of India'
            },
            'indianexpress.com': {
                'title_selectors': ['h1.heading', 'h1.title', 'h1', '.article-title'],
                'date_selectors': ['.date', '.article-date', '.published-on', '.timestamp'],
                'content_selectors': ['.story-details p', '.article-content p', '.story-content p', 'article p'],
                'source_name': 'Indian Express'
            },
            'hindustantimes.com': {
                'title_selectors': ['h1.heading', 'h1.title', 'h1', '.article-title'],
                'date_selectors': ['.date', '.article-date', '.published-on', '.timestamp'],
                'content_selectors': ['.story-content p', '.article-content p', '.story-details p', 'article p'],
                'source_name': 'Hindustan Times'
            },
            'deccanherald.com': {
                'title_selectors': ['h1.heading', 'h1.title', 'h1', '.article-title'],
                'date_selectors': ['.date', '.article-date', '.published-on', '.timestamp'],
                'content_selectors': ['.story-content p', '.article-content p', '.story-details p', 'article p'],
                'source_name': 'Deccan Herald'
            }
        }
    
    def scrape_urls(self, urls: List[str]) -> List[Dict]:
        """
        Scrape articles from a list of URLs
        
        Args:
            urls: List of article URLs to scrape
            
        Returns:
            List of scraped article data
        """
        articles = []
        
        logger.info(f"Starting to scrape {len(urls)} URLs")
        
        for i, url in enumerate(urls, 1):
            logger.info(f"Scraping URL {i}/{len(urls)}: {url}")
            
            try:
                article_data = self._scrape_single_url(url)
                if article_data:
                    articles.append(article_data)
                    logger.info(f"Successfully scraped: {article_data.get('title', 'Unknown title')[:50]}...")
                else:
                    logger.warning(f"No content found for: {url}")
                    
            except Exception as e:
                logger.error(f"Error scraping {url}: {str(e)}")
                continue
            
            # Add delay between requests
            time.sleep(2)
        
        logger.info(f"Successfully scraped {len(articles)} out of {len(urls)} URLs")
        return articles
    
    def _scrape_single_url(self, url: str) -> Optional[Dict]:
        """
        Scrape a single article URL
        """
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Determine site configuration
            domain = urlparse(url).netloc.lower()
            site_config = self._get_site_config(domain)
            
            # Extract article data
            title = self._extract_text_with_selectors(soup, site_config['title_selectors'])
            date = self._extract_text_with_selectors(soup, site_config['date_selectors'])
            content = self._extract_content_with_selectors(soup, site_config['content_selectors'])
            
            if not title or not content:
                return None
            
            # Check temporal scope
            if not self._is_within_temporal_scope(date):
                logger.info(f"Article {url} is outside temporal scope (2000-2025), skipping")
                return None
            
            return {
                'url': url,
                'title': title.strip(),
                'date': self._parse_date(date),
                'source': site_config['source_name'],
                'content': content.strip()
            }
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return None
    
    def _get_site_config(self, domain: str) -> Dict:
        """
        Get site configuration based on domain
        """
        for site_domain, config in self.site_configs.items():
            if site_domain in domain:
                return config
        
        # Default configuration for unknown sites
        return {
            'title_selectors': ['h1', '.title', '.article-title'],
            'date_selectors': ['.date', '.article-date', '.published-on'],
            'content_selectors': ['article p', '.content p', '.article-content p'],
            'source_name': 'Unknown Source'
        }
    
    def _extract_text_with_selectors(self, soup: BeautifulSoup, selectors: List[str]) -> str:
        """
        Extract text using multiple CSS selectors
        """
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        return ""
    
    def _extract_content_with_selectors(self, soup: BeautifulSoup, selectors: List[str]) -> str:
        """
        Extract article content using multiple CSS selectors
        """
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                content = " ".join([elem.get_text().strip() for elem in elements])
                if content:
                    return content
        return ""
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """
        Parse date string to standardized format
        """
        if not date_str:
            return None
        
        # Use date patterns from config
        for pattern in DATE_PATTERNS:
            match = re.search(pattern, date_str)
            if match:
                try:
                    if len(match.groups()) == 3:
                        # Try to parse the date
                        parsed_date = datetime.strptime(match.group(0), pattern.replace('\\', ''))
                        return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
        
        return date_str  # Return original if parsing fails
    
    def _is_within_temporal_scope(self, date_str: str) -> bool:
        """
        Check if article date falls within the specified temporal scope (2000-2025)
        """
        if not FILTER_BY_DATE or not date_str:
            return True
        
        try:
            # Try to extract year from various date formats
            year_match = re.search(r'(\d{4})', date_str)
            if year_match:
                year = int(year_match.group(1))
                return START_YEAR <= year <= END_YEAR
            
            # If no year found, try to parse the full date
            parsed_date = self._parse_date(date_str)
            if parsed_date:
                year = int(parsed_date.split('-')[0])
                return START_YEAR <= year <= END_YEAR
                
        except (ValueError, IndexError, AttributeError):
            pass
        
        # If we can't determine the year, include the article (better to be inclusive)
        logger.warning(f"Could not determine year for date: {date_str}")
        return True


class ElephantDataExtractor:
    """
    Extract structured data from article content using NLP and regex
    """
    
    def __init__(self, nlp_model):
        self.nlp = nlp_model
        
        # Central India states and districts (from config)
        self.states = CENTRAL_INDIA_STATES
        self.districts = CENTRAL_INDIA_DISTRICTS
        
        # Regex patterns for data extraction (from config)
        self.patterns = EXTRACTION_PATTERNS
    
    def extract_structured_data(self, article_data: Dict) -> Dict:
        """
        Extract structured data from article content
        """
        content = article_data.get('content', '')
        title = article_data.get('title', '')
        full_text = f"{title} {content}"
        
        # Initialize result dictionary
        result = {
            'Date': article_data.get('date'),
            'State': None,
            'District': None,
            'Block': None,
            'Village': None,
            'No. of Elephants': None,
            'Type of Incident': None,
            'Human Deaths': None,
            'Elephant Deaths': None,
            'Damage (Crop/Property/Other)': None,
            'Source': article_data.get('source'),
            'URL': article_data.get('url')
        }
        
        # Extract location information using spaCy NER
        location_info = self._extract_locations(full_text)
        result.update(location_info)
        
        # Extract numeric data using regex
        result['No. of Elephants'] = self._extract_number(full_text, self.patterns['elephant_count'])
        result['Human Deaths'] = self._extract_number(full_text, self.patterns['human_deaths'])
        result['Elephant Deaths'] = self._extract_number(full_text, self.patterns['elephant_deaths'])
        
        # Extract incident type
        result['Type of Incident'] = self._extract_incident_type(full_text)
        
        # Extract damage type
        result['Damage (Crop/Property/Other)'] = self._extract_damage_type(full_text)
        
        return result
    
    def _extract_locations(self, text: str) -> Dict:
        """
        Extract location information using spaCy NER
        """
        doc = self.nlp(text)
        
        locations = {
            'State': None,
            'District': None,
            'Block': None,
            'Village': None
        }
        
        # Extract entities
        for ent in doc.ents:
            if ent.label_ == "GPE":  # Geopolitical entity
                entity_text = ent.text.strip()
                
                # Check if it's a state
                for state in self.states:
                    if state.lower() in entity_text.lower() or entity_text.lower() in state.lower():
                        locations['State'] = state
                        break
                
                # Check if it's a district
                for district in self.districts:
                    if district.lower() in entity_text.lower() or entity_text.lower() in district.lower():
                        locations['District'] = district
                        break
                
                # Check for village/block patterns
                if any(keyword in entity_text.lower() for keyword in ['village', 'block', 'tehsil', 'taluka']):
                    if 'village' in entity_text.lower():
                        locations['Village'] = entity_text
                    elif any(keyword in entity_text.lower() for keyword in ['block', 'tehsil', 'taluka']):
                        locations['Block'] = entity_text
        
        return locations
    
    def _extract_number(self, text: str, patterns: List[str]) -> Optional[int]:
        """
        Extract number using regex patterns
        """
        text_lower = text.lower()
        
        # First try numeric patterns
        for pattern in patterns:
            if pattern.startswith(r'(\d+'):
                matches = re.findall(pattern, text_lower)
                if matches:
                    try:
                        return int(matches[0])
                    except (ValueError, IndexError):
                        continue
        
        # Then try text-based patterns
        text_numbers = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
        }
        
        for pattern in patterns:
            if not pattern.startswith(r'(\d+'):
                matches = re.findall(pattern, text_lower)
                if matches:
                    match_text = matches[0].lower()
                    for word, num in text_numbers.items():
                        if word in match_text:
                            return num
        
        return None
    
    def _extract_incident_type(self, text: str) -> Optional[str]:
        """
        Extract incident type from text
        """
        text_lower = text.lower()
        
        for incident_type in self.patterns['incident_types']:
            if incident_type in text_lower:
                return incident_type.title()
        
        return None
    
    def _extract_damage_type(self, text: str) -> Optional[str]:
        """
        Extract damage type from text
        """
        text_lower = text.lower()
        
        damage_found = []
        for damage_type in self.patterns['damage_types']:
            if damage_type in text_lower:
                damage_found.append(damage_type.title())
        
        if damage_found:
            return ', '.join(damage_found)
        
        return None


def main():
    """
    Main function to run the manual URL scraper
    """
    # Initialize scraper and extractor
    scraper = ManualURLScraper()
    extractor = ElephantDataExtractor(scraper.nlp)
    
    # Get URLs from user
    print("Manual URL Scraper for Elephant News Articles")
    print("=" * 50)
    print("Enter article URLs (one per line). Press Enter twice when done:")
    print()
    
    urls = []
    while True:
        url = input("URL: ").strip()
        if not url:
            break
        urls.append(url)
    
    if not urls:
        print("No URLs provided. Exiting.")
        return
    
    print(f"\nProcessing {len(urls)} URLs...")
    
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
    filename = f"manual_elephant_data_{timestamp}.csv"
    
    df.to_csv(filename, index=False, encoding='utf-8')
    logger.info(f"Data saved to {filename}")
    
    # Display summary
    print(f"\n{'='*60}")
    print(f"MANUAL URL SCRAPING COMPLETED")
    print(f"{'='*60}")
    print(f"URLs processed: {len(urls)}")
    print(f"Articles scraped: {len(articles)}")
    print(f"Articles processed: {len(structured_data)}")
    print(f"Data saved to: {filename}")
    
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
