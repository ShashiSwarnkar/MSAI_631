"""
Web Scraper for Review Sites
Provides local alternative to Google Custom Search API
"""
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import quote_plus

class ReviewSiteScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.cache = {}
    
    def search(self, query, sites, max_results=5):
        """
        Search review sites for query.
        Returns list of results similar to Google Custom Search format.
        """
        all_results = []
        
        for site in sites:
            try:
                results = self._search_site(site, query)
                all_results.extend(results)
                time.sleep(1)  # Be respectful to servers
            except Exception as e:
                print(f"Error searching {site}: {e}")
        
        return all_results[:max_results]
    
    def _search_site(self, site, query):
        """Search a specific site using DuckDuckGo site search."""
        # Use DuckDuckGo HTML search (no API key needed)
        search_query = f"{query} site:{site}"
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(search_query)}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            # Parse DuckDuckGo results
            for result in soup.find_all('div', class_='result', limit=3):
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')
                
                if title_elem:
                    results.append({
                        'title': title_elem.get_text(strip=True),
                        'snippet': snippet_elem.get_text(strip=True) if snippet_elem else '',
                        'link': title_elem.get('href', ''),
                    })
            
            return results
        except Exception as e:
            print(f"Scraping error for {site}: {e}")
            return []
    
    def get_sites_for_category(self, category):
        """Get review sites for category (same as cloud version)."""
        site_mappings = {
            'electronics': ['wirecutter.com', 'rtings.com'],
            'home': ['consumerreports.org', 'goodhousekeeping.com'],
            'fashion': ['whowhatwear.com', 'vogue.com']
        }
        return site_mappings.get(category, ['wirecutter.com', 'rtings.com'])
