"""
Test the elephant scraper with sample data
"""

from elephant_scraper import ElephantNewsScraper, ElephantDataExtractor

def test_with_sample_data():
    """Test the scraper with sample data"""
    
    print("Testing Elephant News Scraper with Sample Data")
    print("=" * 50)
    
    # Initialize scraper and extractor
    scraper = ElephantNewsScraper()
    extractor = ElephantDataExtractor(scraper.nlp)
    
    # Sample articles
    sample_articles = [
        {
            'url': 'https://example.com/sample1',
            'title': 'Three elephants spotted in Bastar district, Chhattisgarh',
            'date': '2024-01-15',
            'source': 'sample_data',
            'content': 'Three elephants were sighted near the village of Kondagaon in Bastar district, Chhattisgarh. The elephants caused crop damage to local farmers. Forest officials are monitoring the situation.'
        },
        {
            'url': 'https://example.com/sample2',
            'title': 'Elephant attack kills two people in Madhya Pradesh',
            'date': '2024-02-20',
            'source': 'sample_data',
            'content': 'Two people were killed when an elephant attacked them in Seoni district, Madhya Pradesh. The incident occurred when the victims were working in their field. Forest department has launched an investigation.'
        },
        {
            'url': 'https://example.com/sample3',
            'title': 'Elephant herd enters village in Maharashtra',
            'date': '2024-03-10',
            'source': 'sample_data',
            'content': 'A herd of five elephants entered a village in Gadchiroli district, Maharashtra. The elephants damaged several houses and crops. No human casualties were reported.'
        },
        {
            'url': 'https://example.com/sample4',
            'title': 'Dead elephant found in Telangana forest',
            'date': '2024-04-05',
            'source': 'sample_data',
            'content': 'A dead elephant was found in Adilabad district, Telangana. The cause of death is under investigation. Forest officials suspect natural causes.'
        },
        {
            'url': 'https://example.com/sample5',
            'title': 'Human-elephant conflict escalates in Andhra Pradesh',
            'date': '2024-05-12',
            'source': 'sample_data',
            'content': 'Human-elephant conflict has escalated in Visakhapatnam district, Andhra Pradesh. Elephants have been raiding crops and causing property damage. Local authorities are working on mitigation measures.'
        }
    ]
    
    # Extract structured data
    structured_data = []
    for i, article in enumerate(sample_articles, 1):
        print(f"\nProcessing sample article {i}: {article['title']}")
        
        try:
            structured_article = extractor.extract_structured_data(article)
            structured_data.append(structured_article)
            
            # Display extracted data
            print(f"  State: {structured_article['State']}")
            print(f"  District: {structured_article['District']}")
            print(f"  No. of Elephants: {structured_article['No. of Elephants']}")
            print(f"  Type of Incident: {structured_article['Type of Incident']}")
            print(f"  Human Deaths: {structured_article['Human Deaths']}")
            print(f"  Elephant Deaths: {structured_article['Elephant Deaths']}")
            print(f"  Damage: {structured_article['Damage (Crop/Property/Other)']}")
            
        except Exception as e:
            print(f"  Error processing article: {str(e)}")
            continue
    
    # Create DataFrame and save to CSV
    import pandas as pd
    df = pd.DataFrame(structured_data)
    
    # Generate filename with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sample_elephant_data_{timestamp}.csv"
    
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"\nSample data saved to {filename}")
    
    # Display summary
    print(f"\n{'='*50}")
    print(f"SAMPLE DATA PROCESSING COMPLETED")
    print(f"{'='*50}")
    print(f"Articles processed: {len(structured_data)}")
    print(f"Data saved to: {filename}")
    
    # Display sample data
    if len(df) > 0:
        print(f"\nSample Data:")
        print(df.to_string())
        
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
    test_with_sample_data()
