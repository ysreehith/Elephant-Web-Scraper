# Elephant Range Extension Research - Manual URL Scraper

A specialized scraper for processing manually curated elephant-related news articles from Central India (Madhya Pradesh, Chhattisgarh, Telangana, Andhra Pradesh, Maharashtra) to support research on elephant range extension patterns.

## Features

- **Manual URL processing**: Process articles from URLs you provide
- **Multi-site support**: Works with The Hindu, Times of India, Indian Express, and more
- **Temporal filtering**: Focuses on news reports from 2000-2025 (last two decades)
- **Intelligent data extraction**: Uses spaCy NLP and regex patterns
- **Structured output**: Generates CSV datasets with standardized fields
- **Error handling**: Robust handling of network issues and parsing errors
- **Quality control**: You choose which articles to analyze

## Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install spaCy language model**:
   ```bash
   python -m spacy download en_core_web_sm
   ```

3. **Test the installation**:
   ```bash
   python test_sample_data.py
   ```

## Usage

### Method 1: Interactive URL Input
```bash
python manual_url_scraper.py
```
- Enter URLs one by one when prompted
- Press Enter twice when done
- Scraper processes all URLs and generates CSV

### Method 2: File-Based URL Processing
```bash
python scrape_from_file.py
```
- Create a text file with URLs (one per line)
- Run the script and specify the filename
- Scraper processes all URLs from the file

### Example URL File Format
Create a text file (e.g., `urls.txt`) with URLs:
```
# Sample Elephant News Article URLs
https://www.thehindu.com/news/national/elephant-sighting-in-bastar/article12345678.ece
https://timesofindia.indiatimes.com/city/raipur/elephant-attack-kills-two/articleshow/12345678.cms
https://indianexpress.com/article/india/elephant-herd-enters-village-12345678/
```

## Output Format

The scraper generates CSV files with the following columns:

| Column | Description |
|--------|-------------|
| Date | Publication date |
| State | Indian state (extracted via NLP) |
| District | District name (extracted via NLP) |
| Block | Block/Tehsil name (extracted via NLP) |
| Village | Village name (extracted via NLP) |
| No. of Elephants | Number of elephants mentioned |
| Type of Incident | Type of incident (sighting, conflict, etc.) |
| Human Deaths | Number of human deaths |
| Elephant Deaths | Number of elephant deaths |
| Damage (Crop/Property/Other) | Type of damage caused |
| Source | News source (the_hindu, times_of_india) |
| URL | Article URL |

## Data Extraction Methods

### Temporal Filtering
- Automatically filters articles to 2000-2025 timeframe
- Supports various date formats commonly found in news articles
- Configurable temporal scope via `config.py`
- Skips articles outside the specified date range

### Location Extraction
- Uses spaCy Named Entity Recognition (NER)
- Recognizes Central India states: Madhya Pradesh, Chhattisgarh, Telangana, Andhra Pradesh, Maharashtra
- Identifies districts, villages, blocks, and tehsils within these states

### Numeric Data Extraction
- Regex patterns for elephant counts
- Human and elephant death counts
- Damage quantification

### Incident Classification
- Keyword-based incident type detection
- Damage type categorization
- Conflict severity assessment

## Supported News Sources

### The Hindu
- Search URL: `https://www.thehindu.com/search/?q={query}&order=DESC&sort=publishdate&page={page}`
- Article selectors configured for current site structure

### Times of India
- Search URL: `https://timesofindia.indiatimes.com/topic/{query}/{page}`
- Article selectors configured for current site structure

## Configuration

### Predefined Search Keywords

The scraper automatically searches using 25 focused keywords covering:

**Core Sightings:**
- "elephant sighting", "elephant spotted", "elephant found", "elephant herd"

**Location-Specific:**
- "elephant entered village", "elephant entered district", "elephant entered block"

**Deaths & Mortality:**
- "elephant death", "elephant deaths", "elephant killed", "dead elephant"

**Human-Elephant Conflicts:**
- "human elephant conflict", "elephant attack", "elephant trampled"

**Crop & Property Damage:**
- "crop damage elephant", "elephant crop damage", "elephant property damage"

**State-Specific:**
- "elephant Chhattisgarh", "elephant Madhya Pradesh", "elephant Maharashtra", etc.

**Conflict & Incidents:**
- "elephant conflict", "elephant incident", "elephant raid", "elephant encounter"

### Temporal Scope Settings

Edit `config.py` to modify temporal filtering:

```python
# Temporal scope configuration
START_YEAR = 2000
END_YEAR = 2025
FILTER_BY_DATE = True  # Set to False to include all dates
```

### Geographic Scope

The scraper is configured for Central India states:
- Madhya Pradesh
- Chhattisgarh  
- Telangana
- Andhra Pradesh
- Maharashtra

## Extending the Scraper

### Adding New News Sources

1. Add site configuration to `news_sites` dictionary in `ElephantNewsScraper.__init__()`
2. Define CSS selectors for article elements
3. Test with sample searches

### Improving Data Extraction

1. Add new regex patterns to `ElephantDataExtractor.patterns`
2. Enhance location recognition with additional place names
3. Improve incident classification logic

## Error Handling

The scraper includes comprehensive error handling for:
- Network timeouts and connection errors
- Invalid HTML parsing
- Missing article elements
- Date parsing failures
- NLP processing errors

## Performance Considerations

- Rate limiting between requests (2-second delays)
- Session reuse for efficient connections
- Robust timeout handling
- Memory-efficient processing

## Research Applications

This scraper supports research on:
- Elephant range extension patterns in Central India
- Human-elephant conflict analysis across five states
- Temporal trends in elephant sightings
- Geographic distribution of incidents in Central India
- Impact assessment of elephant movements

## Dependencies

- **requests**: HTTP library for web scraping
- **beautifulsoup4**: HTML parsing
- **pandas**: Data manipulation and CSV export
- **spacy**: Natural language processing
- **lxml**: XML/HTML parser
- **urllib3**: HTTP client

## License

This project is developed for academic research purposes.

## Contributing

To contribute to this project:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Troubleshooting

### Common Issues

1. **spaCy model not found**:
   ```bash
   python -m spacy download en_core_web_sm
   ```

2. **Network timeout errors**:
   - Check internet connection
   - Increase timeout values in the code
   - Verify website accessibility

3. **No articles found**:
   - Try different search keywords
   - Check if news sites have changed their structure
   - Verify CSS selectors are still valid

### Getting Help

For issues or questions:
1. Check the logs for error messages
2. Verify all dependencies are installed
3. Test with simple keywords first
4. Review the configuration settings
