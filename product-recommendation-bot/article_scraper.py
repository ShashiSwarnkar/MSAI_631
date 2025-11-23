"""
Article Scraper for Product Reviews
Scrapes full article content and uses LLM to extract detailed product information.
"""
import requests
from bs4 import BeautifulSoup
import json
import time
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArticleScraper:
    def __init__(self, llm_provider=None):
        """
        Initialize the scraper.
        
        Args:
            llm_provider: Function or object with .generate() method to process text.
                          If None, extraction will return raw text.
        """
        self.llm_provider = llm_provider
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        self.cache = {}

    def scrape_and_extract(self, url, query):
        """
        Scrape an article and extract product recommendations relevant to the query.
        """
        if url in self.cache:
            logger.info(f"Using cached article for: {url}")
            return self.cache[url]

        logger.info(f"Scraping article: {url}")
        content = self._fetch_article(url)
        
        if not content:
            return []

        # Extract products using LLM
        products = self._extract_products_with_llm(content, query, url)
        
        # Cache results
        if products:
            self.cache[url] = products
            
        return products

    def _fetch_article(self, url):
        """Fetch and parse article HTML."""
        try:
            time.sleep(1)  # Polite delay
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()

            # Site-specific parsing
            domain = url.lower()
            if 'wirecutter' in domain:
                text = self._parse_wirecutter(soup)
            elif 'rtings' in domain:
                text = self._parse_rtings(soup)
            elif 'consumerreports' in domain:
                text = self._parse_consumer_reports(soup)
            else:
                # Generic fallback
                article_body = soup.find('article') or \
                               soup.find('main') or \
                               soup.find('div', class_=re.compile(r'content|article|body|entry', re.I)) or \
                               soup.body

                if article_body:
                    text = article_body.get_text(separator='\n', strip=True)
                else:
                    text = soup.get_text(separator='\n', strip=True)

            # Clean up text (remove excessive newlines)
            text = re.sub(r'\n{3,}', '\n\n', text)
            
            # Truncate if too long (to fit in LLM context)
            return text[:15000]
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None

    def _parse_wirecutter(self, soup):
        """Extract content from Wirecutter articles."""
        # Wirecutter often uses specific data-attributes or classes
        content = []
        
        # Title
        title = soup.find('h1')
        if title:
            content.append(title.get_text(strip=True))
            
        # Intro
        intro = soup.find('p', class_=re.compile(r'intro', re.I))
        if intro:
            content.append(intro.get_text(strip=True))
            
        # Product cards/picks
        # Look for "Our Pick", "Runner Up", etc.
        for pick in soup.find_all(['h2', 'h3', 'h4']):
            text = pick.get_text(strip=True)
            if any(x in text.lower() for x in ['pick', 'runner', 'upgrade', 'budget', 'also great']):
                content.append(f"\n--- {text} ---\n")
                # Get following siblings until next header
                curr = pick.find_next_sibling()
                while curr and curr.name not in ['h2', 'h3', 'h4']:
                    if curr.name in ['p', 'ul', 'div']:
                        content.append(curr.get_text(strip=True))
                    curr = curr.find_next_sibling()
                    
        # If specific parsing didn't find much, fall back to generic article body
        if len(content) < 3:
            article = soup.find('article') or soup.find('main')
            if article:
                return article.get_text(separator='\n', strip=True)
                
        return '\n\n'.join(content)

    def _parse_rtings(self, soup):
        """Extract content from RTINGS reviews."""
        # RTINGS is very structured with test results
        content = []
        
        title = soup.find('h1')
        if title:
            content.append(title.get_text(strip=True))
            
        # Verdict / Mixed Usage
        verdict = soup.find('div', class_=re.compile(r'verdict', re.I))
        if verdict:
            content.append("VERDICT: " + verdict.get_text(separator='\n', strip=True))
            
        # Test results often in tables or specific divs
        for section in soup.find_all('div', class_='test_group'):
            header = section.find('h2')
            if header:
                content.append(f"\n{header.get_text(strip=True)}")
                score = section.find('div', class_='score')
                if score:
                    content.append(f"Score: {score.get_text(strip=True)}")
                desc = section.find('p')
                if desc:
                    content.append(desc.get_text(strip=True))
                    
        if len(content) < 3:
             return soup.get_text(separator='\n', strip=True)
             
        return '\n\n'.join(content)

    def _parse_consumer_reports(self, soup):
        """Extract content from Consumer Reports."""
        # Often has a list of products
        content = []
        
        title = soup.find('h1')
        if title:
            content.append(title.get_text(strip=True))
            
        # Product cards
        products = soup.find_all('div', class_=re.compile(r'product-card|entry-content', re.I))
        for p in products:
            content.append(p.get_text(separator='\n', strip=True))
            
        if not content:
            return soup.get_text(separator='\n', strip=True)
            
        return '\n\n'.join(content)

    def _extract_products_with_llm(self, content, query, url):
        """Use LLM to extract structured product data from text."""
        if not self.llm_provider:
            logger.warning("No LLM provider configured for extraction")
            return []

        prompt = f"""
        Analyze the following product review article text and extract the top recommended products relevant to the user's query: "{query}".
        
        Article Content (truncated):
        {content}
        
        Extract up to 5 products in this specific JSON format:
        [
            {{
                "name": "Product Name",
                "price": "Price string (e.g. $199)",
                "pros": "Key pros (comma separated)",
                "cons": "Key cons (comma separated)",
                "description": "Brief description of why it's good",
                "rating": "Score if available (e.g. 8/10 or 4.5/5), else null",
                "award": "Any award mentioned (e.g. 'Top Pick', 'Best Budget')",
                "source_url": "{url}"
            }}
        ]
        
        Rules:
        1. Only include products clearly recommended or reviewed.
        2. If the text is not a review or contains no products, return [].
        3. Return ONLY valid JSON.
        """

        try:
            # Handle different LLM provider types
            if hasattr(self.llm_provider, 'generate'):
                # LocalLLM instance
                response = self.llm_provider.generate(prompt, temperature=0.1)
            elif callable(self.llm_provider):
                # Function (like _call_gemini_api)
                response = self.llm_provider(prompt)
            else:
                logger.error("Invalid LLM provider type")
                return []

            if not response:
                return []

            # Clean JSON
            response = response.strip()
            
            # Try to find JSON array pattern
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                response = json_match.group(0)
            elif '```json' in response:
                response = response.split('```json')[1].split('```')[0]
            elif '```' in response:
                response = response.split('```')[1].split('```')[0]
            
            # Remove any trailing commas before closing brackets (common LLM error)
            response = re.sub(r',\s*]', ']', response)
            response = re.sub(r',\s*}', '}', response)
            
            return json.loads(response.strip())
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"Raw response: {response}")
            return []
        except Exception as e:
            logger.error(f"Error in LLM extraction: {e}")
            return []

if __name__ == "__main__":
    # Simple test if run directly
    print("ArticleScraper module ready.")
