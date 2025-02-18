# twitter_scrape/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

# API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CSE_ID = os.getenv("CSE_ID")
SEARCH_BASE_URL = "https://www.googleapis.com/customsearch/v1"

# Search Parameters
DEFAULT_RESULTS_NUM = 10  # Max 10 for free tier
TWITTER_DOMAIN_FILTER = "site:twitter.com"

# Scraping Parameters
MAX_RETRIES = 3
REQUEST_DELAY = 2  # Seconds between API calls