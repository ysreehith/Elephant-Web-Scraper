"""
Configuration file for Elephant News Scraper
"""

# Search configuration - Focused keyword set for elephant research
DEFAULT_KEYWORDS = [
    # Core sightings and presence
    "elephant sighting",
    "elephant spotted",
    "elephant found",
    "elephant herd",
    
    # Location-specific entries
    "elephant entered village",
    "elephant entered district",
    "elephant entered block",
    
    # Deaths and mortality
    "elephant death",
    "elephant deaths",
    "elephant killed",
    "dead elephant",
    
    # Human-elephant conflicts
    "human elephant conflict",
    "elephant attack",
    "elephant trampled",
    
    # Crop and property damage
    "crop damage elephant",
    "elephant crop damage",
    "elephant property damage",
    
    # State-specific searches
    "elephant Chhattisgarh",
    "elephant Madhya Pradesh", 
    "elephant Maharashtra",
    "elephant Telangana",
    "elephant Andhra Pradesh",
    
    # Conflict and incidents
    "elephant conflict",
    "elephant incident",
    "elephant raid",
    "elephant encounter"
]

# Scraping configuration
MAX_PAGES_PER_SITE = 5
REQUEST_TIMEOUT = 10
DELAY_BETWEEN_REQUESTS = 2
MAX_RETRIES = 3

# Temporal scope configuration
START_YEAR = 2000
END_YEAR = 2025
FILTER_BY_DATE = True  # Set to False to include all dates

# Output configuration
OUTPUT_DIRECTORY = "output"
CSV_ENCODING = "utf-8"
INCLUDE_TIMESTAMP_IN_FILENAME = True

# News site configurations
NEWS_SITES_CONFIG = {
    'the_hindu': {
        'enabled': True,
        'base_url': 'https://www.thehindu.com',
        'search_url': 'https://www.thehindu.com/search/?q={query}&order=DESC&sort=publishdate&page={page}',
        'article_selectors': {
            'title': 'h1.title',
            'date': '.publish-time',
            'content': '.article-content p',
            'links': '.story-card-news a'
        }
    },
    'times_of_india': {
        'enabled': True,
        'base_url': 'https://timesofindia.indiatimes.com',
        'search_url': 'https://timesofindia.indiatimes.com/topic/{query}/{page}',
        'article_selectors': {
            'title': 'h1._1Y-96',
            'date': '._3Mkg-',
            'content': '._3YYSt p',
            'links': '.content a'
        }
    }
}

# Location data for Central India
CENTRAL_INDIA_STATES = [
    'Madhya Pradesh', 'Chhattisgarh', 'Telangana', 'Andhra Pradesh', 'Maharashtra'
]

CENTRAL_INDIA_DISTRICTS = [
    # Chhattisgarh
    'Bastar', 'Dantewada', 'Bijapur', 'Narayanpur', 'Kanker', 'Kondagaon',
    'Sukma', 'Jagdalpur', 'Dhamtari', 'Raipur', 'Bilaspur', 'Korba',
    'Raigarh', 'Janjgir-Champa', 'Mungeli', 'Kabirdham', 'Balod',
    'Baloda Bazar', 'Gariaband', 'Mahasamund', 'Durg', 'Rajnandgaon',
    
    # Madhya Pradesh
    'Balaghat', 'Mandla', 'Seoni', 'Chhindwara', 'Betul', 'Hoshangabad',
    'Narsinghpur', 'Jabalpur', 'Katni', 'Rewa', 'Satna', 'Panna',
    'Damoh', 'Sagar', 'Tikamgarh', 'Chhatarpur', 'Shivpuri', 'Guna',
    'Ashoknagar', 'Vidisha', 'Raisen', 'Sehore', 'Bhopal', 'Rajgarh',
    
    # Maharashtra
    'Gadchiroli', 'Chandrapur', 'Nagpur', 'Bhandara', 'Gondia',
    'Amravati', 'Wardha', 'Yavatmal', 'Washim', 'Akola',
    'Buldhana', 'Aurangabad', 'Jalna', 'Parbhani', 'Hingoli',
    'Nanded', 'Latur', 'Osmanabad', 'Beed', 'Ahmednagar',
    
    # Telangana
    'Adilabad', 'Nirmal', 'Mancherial', 'Komaram Bheem Asifabad',
    'Nizamabad', 'Kamareddy', 'Karimnagar', 'Jagtial', 'Peddapalli',
    'Rajanna Sircilla', 'Sangareddy', 'Medak', 'Siddipet', 'Jangaon',
    'Warangal Urban', 'Warangal Rural', 'Mahbubabad', 'Khammam',
    'Bhadradri Kothagudem', 'Hyderabad', 'Rangareddy', 'Vikarabad',
    'Mahabubnagar', 'Nagarkurnool', 'Wanaparthy', 'Jogulamba Gadwal',
    'Narayanpet', 'Suryapet', 'Yadadri Bhuvanagiri', 'Nalgonda',
    
    # Andhra Pradesh
    'Srikakulam', 'Vizianagaram', 'Visakhapatnam', 'East Godavari',
    'West Godavari', 'Krishna', 'Guntur', 'Prakasam', 'Nellore',
    'Chittoor', 'YSR Kadapa', 'Annamayya', 'Sri Sathya Sai',
    'Kurnool', 'Nandyal', 'Anantapur', 'Tirupati'
]

# Regex patterns for data extraction
EXTRACTION_PATTERNS = {
    'elephant_count': [
        r'(\d+)\s*elephants?',
        r'(\d+)\s*pachyderms?',
        r'(\d+)\s*jumbos?',
        r'(\d+)\s*herd',
        r'herd\s*of\s*(\d+)',
        r'(\d+)\s*members?',
        r'(\d+)\s*animals?',
        r'three\s*elephants?',
        r'five\s*elephants?',
        r'two\s*elephants?',
        r'one\s*elephant'
    ],
    'human_deaths': [
        r'(\d+)\s*people?\s*killed',
        r'(\d+)\s*persons?\s*killed',
        r'(\d+)\s*deaths?',
        r'(\d+)\s*fatalities?',
        r'killed\s*(\d+)',
        r'(\d+)\s*dead',
        r'(\d+)\s*victims?',
        r'two\s*people?\s*killed',
        r'one\s*person?\s*killed',
        r'kills?\s*two\s*people?',
        r'kills?\s*one\s*person?'
    ],
    'elephant_deaths': [
        r'(\d+)\s*elephants?\s*killed',
        r'(\d+)\s*elephants?\s*dead',
        r'(\d+)\s*pachyderms?\s*killed',
        r'elephant\s*was\s*found\s*dead',
        r'elephant\s*death',
        r'(\d+)\s*jumbos?\s*killed',
        r'(\d+)\s*elephants?\s*died',
        r'dead\s*elephant',
        r'elephant\s*found\s*dead'
    ],
    'incident_types': [
        'sighting', 'crop damage', 'property damage', 'human death',
        'elephant death', 'conflict', 'attack', 'raid', 'trespass',
        'encounter', 'rampage', 'stampede', 'collision', 'injury',
        'spotted', 'found', 'entered', 'killed', 'trampled'
    ],
    'damage_types': [
        'crop', 'property', 'house', 'field', 'plantation',
        'vegetation', 'infrastructure', 'vehicle', 'fence', 'wall',
        'houses', 'crops', 'fields'
    ]
}

# Date parsing patterns
DATE_PATTERNS = [
    r'(\d{1,2})/(\d{1,2})/(\d{4})',
    r'(\d{1,2})-(\d{1,2})-(\d{4})',
    r'(\d{4})-(\d{1,2})-(\d{1,2})',
    r'(\w+)\s+(\d{1,2}),\s+(\d{4})',
    r'(\d{1,2})\s+(\w+)\s+(\d{4})',
    r'(\w+)\s+(\d{1,2})\s+(\d{4})',
    r'(\d{1,2})\.(\d{1,2})\.(\d{4})',
    r'(\d{4})\.(\d{1,2})\.(\d{1,2})'
]

# Gemini API configuration
GEMINI_API_KEY = None  # Set your API key here or as environment variable
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_MAX_RETRIES = 3
GEMINI_TIMEOUT = 30

# Gemini extraction prompt template
GEMINI_EXTRACTION_PROMPT = """
You are an expert data extraction specialist. Extract structured information about elephant incidents from the following news article.

Article Text: {article_text}
Source URL: {url}
Source Domain: {source}

Please extract the following information and return ONLY a valid JSON object with these exact field names:

{{
    "Date": "YYYY-MM-DD format or null if not available",
    "State": "One of: Madhya Pradesh, Chhattisgarh, Telangana, Andhra Pradesh, Maharashtra (or null if not mentioned or not in these states)",
    "District": "District name or null if not available",
    "Block": "Block/Tehsil name or null if not available", 
    "Village": "Village name or null if not available",
    "No. of Elephants": "Number of elephants involved (integer or null)",
    "Type of Incident": "Type of incident (e.g., attack, death, crop damage, sighting, etc.) or null",
    "Human Deaths": "Number of human deaths (integer or null)",
    "Elephant Deaths": "Number of elephant deaths (integer or null)",
    "Damage (Crop/Property/Other)": "Type of damage caused or null",
    "Source": "News source name",
    "URL": "Article URL"
}}

Important rules:
1. Only include states from the specified list: Madhya Pradesh, Chhattisgarh, Telangana, Andhra Pradesh, Maharashtra
2. If the article is not about these states, set State to null
3. Focus on incidents from 2000-2025 (last two decades)
4. Extract numbers as integers, not strings
5. If information is not available, use null
6. Return ONLY the JSON object, no additional text or explanation
7. Ensure the JSON is valid and properly formatted
"""

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_FILE = "elephant_scraper.log"
