# twitter_scrape/search_api.py
import requests
import time
from typing import List, Optional
from config import (
    GOOGLE_API_KEY,
    CSE_ID,
    SEARCH_BASE_URL,
    DEFAULT_RESULTS_NUM,
    TWITTER_DOMAIN_FILTER,
    REQUEST_DELAY
)

class GoogleSearchAPI:
    def __init__(self):
        self.last_query_time = 0
        
    def search_tweets(self, query: str, num_results: int = DEFAULT_RESULTS_NUM, 
                     after_date: Optional[str] = None) -> List[str]:
        """
        Search for Twitter content via Google CSE
        Returns list of tweet URLs
        """
        # Rate limiting
        time_since_last = time.time() - self.last_query_time
        if time_since_last < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - time_since_last)
            
        params = {
            "key": GOOGLE_API_KEY,
            "cx": CSE_ID,
            "q": f"{TWITTER_DOMAIN_FILTER} {query}",
            "num": min(num_results, 10),  # Free tier max
            "fields": "items/link"
        }
        
        if after_date:
            params["q"] += f" after:{after_date}"
            
        try:
            response = requests.get(SEARCH_BASE_URL, params=params)
            response.raise_for_status()
            results = response.json().get("items", [])
            
            # Filter for actual tweet URLs
            return [item["link"] for item in results 
                    if "/status/" in item.get("link", "")]
            
        except Exception as e:
            print(f"Search failed: {str(e)}")
            return []