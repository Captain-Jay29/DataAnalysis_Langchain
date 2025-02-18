from playwright.sync_api import sync_playwright
from typing import Optional, Dict
import re
from datetime import datetime

DATE_FORMATS = [
    "%b %d, %Y",  # 'Mar 10, 2024'
    "%I:%M %p · %b %d, %Y"  # '3:45 PM · Mar 10, 2024'
]

def parse_tweet_date(date_str: str) -> Optional[str]:
    """Convert Twitter's date strings to ISO format"""
    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.isoformat()
        except ValueError:
            continue
    return None

def scrape_tweet(url: str, retries: int = 3) -> Optional[Dict]:
    """Scrape public tweet page with retry logic"""
    for attempt in range(retries):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                # Set timeout and wait for network activity
                page.goto(url, timeout=30000, wait_until="networkidle")
                
                # Wait for either the tweet or error message
                try:
                    page.wait_for_selector('article[data-testid="tweet"]', timeout=15000)
                except:
                    # Check if tweet is unavailable
                    if page.query_selector('div[data-testid="error-detail"]'):
                        print(f"Tweet unavailable: {url}")
                        return None
                    
                    # Retry with different selector
                    page.wait_for_selector('div[data-testid="tweetText"]', timeout=15000)
                
                # Extract components
                content = page.query_selector('div[data-testid="tweetText"]')
                username = page.query_selector('a[href^="/"][role="link"] > div > span')
                date_element = page.query_selector('time')
                
                return {
                    "text": content.inner_text() if content else None,
                    "username": username.inner_text() if username else None,
                    "date": parse_tweet_date(date_element.get_attribute("datetime")) if date_element else None,
                    "url": url,
                    "success": True
                }
                
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt == retries - 1:
                    return None
            finally:
                browser.close()