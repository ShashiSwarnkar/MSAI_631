import os
import pandas as pd
import requests
import json
import numpy as np
import pickle
import re
import time
from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
from botbuilder.schema import ChannelAccount, ActivityTypes
from config import DefaultConfig

class ProductRecommendationBot(ActivityHandler):
    def __init__(self, config: DefaultConfig):
        self.config = config
        self.conversation_state = {}  # Store conversation history per user
        self.search_cache = {}  # Cache search results to save API calls
        self.last_search_time = 0  # Track last search for rate limiting
        
    def _get_user_state(self, turn_context: TurnContext):
        """Get or create conversation state for user."""
        user_id = turn_context.activity.from_property.id
        if user_id not in self.conversation_state:
            self.conversation_state[user_id] = {
                'history': [],
                'last_query': None,
                'last_brand': None,
                'last_price_limit': None,
                'last_category': None
            }
        return self.conversation_state[user_id]

    async def on_members_added_activity(
        self, members_added: ChannelAccount, turn_context: TurnContext
    ):
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    "Hello! I'm your Product Recommendation Assistant. I search expert reviews from sites like Wirecutter, RTINGS, and more to find the best products for you. What are you looking for?"
                )

    async def on_message_activity(self, turn_context: TurnContext):
        user_text = turn_context.activity.text
        user_state = self._get_user_state(turn_context)
        
        # Add to conversation history
        user_state['history'].append({'role': 'user', 'text': user_text})
        
        # Search for products using web search
        await turn_context.send_activity("Searching expert reviews for you...")
        
        products = self._web_search_products(user_text, user_state)
        
        if not products:
            response_text = "I couldn't find any expert recommendations for that. Could you try rephrasing or being more specific?"
        else:
            response_text = self._generate_response(user_text, products, user_state)
        
        # Update conversation state
        user_state['last_query'] = user_text
        user_state['history'].append({'role': 'assistant', 'text': response_text})
        
        await turn_context.send_activity(MessageFactory.text(response_text))

    def _web_search_products(self, query, user_state):
        """Search for products using Google Custom Search API."""
        # Build search query with context
        search_query = self._build_search_query(query, user_state)
        
        # Search expert review sites
        search_results = self._google_custom_search(search_query)
        
        if not search_results:
            return []
        
        # Extract product recommendations from search results
        products = self._extract_products_from_results(search_results, query)
        
        return products
    
    def _build_search_query(self, query, user_state):
        """Build optimized search query with context."""
        # Extract intent
        price_limit = self._extract_price_limit(query)
        brand = self._extract_brand(query)
        
        # Update user state
        if price_limit:
            user_state['last_price_limit'] = price_limit
        if brand:
            user_state['last_brand'] = brand
        
        # Build query
        search_terms = []
        
        # Add "best" to get review articles
        if 'best' not in query.lower():
            search_terms.append('best')
        
        search_terms.append(query)
        
        # Add price context
        if price_limit:
            search_terms.append(f'under ${price_limit}')
        
        # Add year for freshness
        search_terms.append('2024')
        
        # Target review sites
        site_filter = 'site:wirecutter.com OR site:rtings.com OR site:consumerreports.org OR site:techradar.com'
        
        final_query = ' '.join(search_terms) + ' ' + site_filter
        
        return final_query
    
    def _google_custom_search(self, query):
        """Perform Google Custom Search with caching and rate limiting."""
        # Check cache first
        if query in self.search_cache:
            print(f"Using cached results for: {query}")
            return self.search_cache[query]
        
        # Rate limiting: wait 2 seconds between searches
        current_time = time.time()
        time_since_last_search = current_time - self.last_search_time
        if time_since_last_search < 2:
            wait_time = 2 - time_since_last_search
            print(f"Rate limiting: waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.config.GOOGLE_SEARCH_API_KEY,
                'cx': self.config.GOOGLE_SEARCH_ENGINE_ID,
                'q': query,
                'num': 5  # Get top 5 results
            }
            
            print(f"Searching Google for: {query}")
            response = requests.get(url, params=params)
            response.raise_for_status()
            result = response.json()
            
            items = result.get('items', [])
            
            # Cache the results
            self.search_cache[query] = items
            self.last_search_time = time.time()
            
            print(f"Found {len(items)} results")
            return items
        except Exception as e:
            print(f"Google Search Error: {e}")
            if hasattr(e, 'response'):
                print(f"Response: {e.response.text}")
            return []
    
    def _extract_products_from_results(self, search_results, original_query):
        """Extract product recommendations from search results using Gemini."""
        products = []
        
        for result in search_results[:3]:  # Process top 3 results
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            link = result.get('link', '')
            
            # Use Gemini to extract product info
            product_info = self._extract_product_info_with_gemini(title, snippet, link, original_query)
            
            if product_info:
                products.extend(product_info)
        
        return products[:5]  # Return top 5 products
    
    def _extract_product_info_with_gemini(self, title, snippet, link, query):
        """Use Gemini to extract structured product information."""
        prompt = f"""Extract product recommendations from this review article snippet.
        
Article Title: {title}
Snippet: {snippet}
User Query: {query}

Extract up to 3 product recommendations in this exact JSON format:
[
  {{
    "name": "Product Name",
    "price": "estimated price in USD (e.g., $299)",
    "pros": "key benefits",
    "source": "review site name",
    "link": "{link}"
  }}
]

If no clear products are mentioned, return an empty array [].
Return ONLY valid JSON, no other text."""

        result = self._call_gemini_api(prompt)
        
        if result:
            try:
                # Clean the response
                result = result.strip()
                if result.startswith('```json'):
                    result = result[7:]
                if result.startswith('```'):
                    result = result[3:]
                if result.endswith('```'):
                    result = result[:-3]
                result = result.strip()
                
                products = json.loads(result)
                return products if isinstance(products, list) else []
            except:
                return []
        return []
    
    def _extract_price_limit(self, query):
        """Extract price limit from query."""
        patterns = [
            r'under\s+\$?(\d+)',
            r'below\s+\$?(\d+)',
            r'less than\s+\$?(\d+)',
            r'(\d+)\s*dollars?\s+or\s+less',
        ]
        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                return int(match.group(1))
        return None
    
    def _extract_brand(self, query):
        """Extract brand name from query."""
        common_brands = ['apple', 'samsung', 'sony', 'bose', 'boat', 'jbl', 'lenovo', 'dell', 'hp', 'asus', 'acer']
        query_lower = query.lower()
        for brand in common_brands:
            if brand in query_lower:
                return brand
        return None

    def _call_gemini_api(self, prompt):
        """Calls Gemini API via REST."""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.config.GEMINI_API_KEY}"
            headers = {'Content-Type': 'application/json'}
            data = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            print(f"Gemini API Error: {e}")
            if hasattr(e, 'response'):
                print(f"Response: {e.response.text}")
            return None

    def _generate_response(self, user_query, products, user_state):
        """Generate personalized recommendation using Gemini."""
        if not products:
            return "I couldn't find any expert recommendations. Try being more specific!"
        
        # Build product list
        product_list_str = ""
        for i, product in enumerate(products, 1):
            name = product.get('name', 'Unknown')
            price = product.get('price', 'N/A')
            pros = product.get('pros', '')
            source = product.get('source', 'Expert review')
            
            product_list_str += f"{i}. **{name}** - {price}\n"
            if pros:
                product_list_str += f"   ✓ {pros}\n"
            product_list_str += f"   Source: {source}\n\n"
        
        # Generate personalized response
        context = ""
        if user_state.get('last_brand'):
            context += f"User prefers {user_state['last_brand']} brand. "
        if user_state.get('last_price_limit'):
            context += f"Budget: under ${user_state['last_price_limit']}. "
        
        prompt = f"""You are a helpful product recommendation assistant. 
        
User asked: "{user_query}"
{context}

Here are expert-recommended products:
{product_list_str}

Provide a helpful, concise recommendation (2-3 sentences). Highlight the best option and why. Be conversational and friendly."""

        result = self._call_gemini_api(prompt)
        
        if result:
            return result + "\n\n" + product_list_str
        return f"Here are the top expert recommendations:\n\n{product_list_str}"
