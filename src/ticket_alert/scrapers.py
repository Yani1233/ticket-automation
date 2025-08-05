"""Alternative scraping methods for cloud environments"""

import os
import logging
import requests
from typing import Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class CloudScraper:
    """Scraper optimized for cloud environments"""
    
    @staticmethod
    def fetch_with_proxy(url: str) -> Optional[str]:
        """Fetch URL using a proxy service (for sites that block cloud IPs)"""
        # Option 1: Use ScraperAPI (free tier available)
        # Sign up at https://www.scraperapi.com/ for free API key
        scraper_api_key = os.getenv('SCRAPER_API_KEY')
        if scraper_api_key:
            proxy_url = f"http://api.scraperapi.com?api_key={scraper_api_key}&url={url}"
            try:
                response = requests.get(proxy_url, timeout=30)
                response.raise_for_status()
                return response.text
            except Exception as e:
                logger.error(f"ScraperAPI error: {e}")
        
        # Option 2: Use free proxy service (less reliable)
        try:
            proxy_url = f"https://api.allorigins.win/raw?url={url}"
            response = requests.get(proxy_url, timeout=20)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Proxy fetch error: {e}")
            return None
    
    @staticmethod
    def check_via_search(movie_name: str, city: str = "bengaluru") -> dict:
        """Check movie availability via search engines (more reliable from cloud)"""
        results = {
            'found': False,
            'platforms': []
        }
        
        # Search for movie + "book tickets" + city
        search_query = f"{movie_name} book tickets {city} site:bookmyshow.com OR site:pvrcinemas.com"
        
        try:
            # Use DuckDuckGo HTML API (no key required)
            ddg_url = f"https://html.duckduckgo.com/html/?q={search_query}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; TicketBot/1.0)'
            }
            
            response = requests.get(ddg_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Check for booking-related results
                for result in soup.find_all('a', class_='result__a'):
                    link_text = result.get_text().lower()
                    if 'book' in link_text or 'tickets' in link_text:
                        results['found'] = True
                        results['platforms'].append(result.get('href', ''))
                        
        except Exception as e:
            logger.error(f"Search check error: {e}")
            
        return results