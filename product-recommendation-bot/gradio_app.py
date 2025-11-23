import gradio as gr
import requests
import json
import re
import time
import os
from dotenv import load_dotenv

# Load environment variables FIRST, before importing config
load_dotenv()


# Now import config (which will read the environment variables)
from config import DefaultConfig


# Import local modules (optional - only used if USE_LOCAL_MODE=true)
try:
    from local_llm import LocalLLM
    from web_scraper import ReviewSiteScraper
    from article_scraper import ArticleScraper
    from conversation_manager import ConversationManager
    LOCAL_MODULES_AVAILABLE = True
except ImportError:
    LOCAL_MODULES_AVAILABLE = False
    print("Local modules not available. Install dependencies: pip install beautifulsoup4 lxml")

class ProductRecommendationChatbot:
    def __init__(self, use_local=None):
        self.config = DefaultConfig()
        
        # Determine mode: use parameter if provided, otherwise use config
        if use_local is None:
            use_local = self.config.USE_LOCAL_MODE
        
        self.use_local = use_local
        self.conversation_history = []
        self.search_cache = {}
        self.last_search_time = 0
        self.user_state = {
            'last_query': None,
            'last_brand': None,
            'last_price_limit': None,
            'last_category': None
        }
        
        # Initialize appropriate backend
        if self.use_local:
            if not LOCAL_MODULES_AVAILABLE:
                raise ImportError("Local mode requires: pip install beautifulsoup4 lxml")
            print("🏠 Using LOCAL mode (Ollama + Web Scraping)")
            self.llm = LocalLLM(model=self.config.LOCAL_LLM_MODEL)
            self.scraper = ReviewSiteScraper()
            self.article_scraper = ArticleScraper(llm_provider=self.llm)
            self.conversation_manager = ConversationManager(llm_provider=self.llm)
            
            # Test Ollama connection
            if not self.llm.test_connection():
                print("⚠️  Ollama not running. Start it and restart the app.")
        else:
            print("☁️  Using CLOUD mode (Gemini + Google Custom Search)")
            self.article_scraper = ArticleScraper(llm_provider=self._call_gemini_api)
            self.conversation_manager = ConversationManager(llm_provider=self._call_gemini_api)
    
    def chat(self, message, history):
        """Main chat function for Gradio."""
        # Add user message to history
        self.conversation_manager.add_message('user', message)
        
        # Check if it's a follow-up question
        is_follow_up = self.conversation_manager.is_follow_up(message)
        
        if is_follow_up:
            print(f"Detected follow-up question: {message}")
            response = self._handle_follow_up(message)
        else:
            # New search
            products = self._web_search_products(message)
            
            if not products:
                response = "I couldn't find any expert recommendations for that. Could you try rephrasing or being more specific?"
            else:
                response = self._generate_response(message, products)
        
        # Update state
        self.user_state['last_query'] = message
        self.conversation_manager.add_message('assistant', response)
        
        return response
        
    def _handle_follow_up(self, message):
        """Handle follow-up questions using conversation context."""
        # Resolve references (e.g., "the first one")
        resolved_message = self.conversation_manager.resolve_reference(message)
        
        # Get context
        context = self.conversation_manager.get_context_for_prompt()
        
        prompt = f"""
        You are a helpful product recommendation assistant.
        
        {context}
        
        User's Follow-up Question: "{resolved_message}"
        
        Answer the question based on the conversation history and products discussed.
        If the user is asking for a comparison, compare the products mentioned.
        If the user asks for a different price/feature, suggest how they might search for that (or if you know, answer it).
        
        Keep it concise and helpful.
        """
        
        if self.use_local:
            response = self.llm.generate(prompt)
        else:
            response = self._call_gemini_api(prompt)
            
        return response if response else "I'm having trouble understanding the follow-up. Could you rephrase?"
    
    def _web_search_products(self, query):
        """Search for products using Google Custom Search API."""
        search_query = self._build_search_query(query)
        search_results = self._google_custom_search(search_query)
        
        if not search_results:
            return []
        
        products = self._extract_products_from_results(search_results, query)
        return products
    
    def _build_search_query(self, query):
        """Build optimized search query with category-specific sites."""
        price_limit = self._extract_price_limit(query)
        brand = self._extract_brand(query)
        
        if price_limit:
            self.user_state['last_price_limit'] = price_limit
        if brand:
            self.user_state['last_brand'] = brand
        
        search_terms = []
        if 'best' not in query.lower():
            search_terms.append('best')
        
        search_terms.append(query)
        
        if price_limit:
            search_terms.append(f'under ${price_limit}')
        
        search_terms.append('2024')
        
        # Category-specific review sites
        category = self._detect_category(query)
        site_filter = self._get_sites_for_category(category)
        
        final_query = ' '.join(search_terms) + ' ' + site_filter
        
        return final_query
    
    def _detect_category(self, query):
        """Detect product category from query."""
        query_lower = query.lower()
        
        # Electronics keywords
        electronics_keywords = [
            'laptop', 'computer', 'phone', 'tablet', 'headphone', 'earbuds', 'speaker',
            'camera', 'tv', 'monitor', 'keyboard', 'mouse', 'gaming', 'console',
            'smartwatch', 'fitness tracker', 'drone', 'router', 'wireless', 'bluetooth'
        ]
        
        # Home goods keywords
        home_keywords = [
            'vacuum', 'blender', 'coffee maker', 'toaster', 'microwave', 'air fryer',
            'mattress', 'pillow', 'sheets', 'towel', 'cookware', 'knife', 'pan',
            'humidifier', 'fan', 'heater', 'air purifier', 'furniture', 'appliance'
        ]
        
        # Fashion keywords
        fashion_keywords = [
            'shoes', 'boots', 'sneakers', 'dress', 'jeans', 'jacket', 'coat',
            'shirt', 'pants', 'bag', 'purse', 'watch', 'sunglasses', 'jewelry',
            'clothing', 'fashion', 'style', 'outfit', 'apparel', 'stylish',
            'winter boots', 'summer dress', 'casual wear', 'formal wear',
            'accessories', 'handbag', 'belt', 'scarf', 'hat', 'gloves'
        ]
        
        # Check for category matches
        for keyword in electronics_keywords:
            if keyword in query_lower:
                return 'electronics'
        
        for keyword in home_keywords:
            if keyword in query_lower:
                return 'home'
        
        for keyword in fashion_keywords:
            if keyword in query_lower:
                return 'fashion'
        
        # Default to electronics if no match
        return 'electronics'
    
    def _get_sites_for_category(self, category):
        """Get review sites for specific category."""
        site_mappings = {
            'electronics': 'site:wirecutter.com OR site:rtings.com',
            'home': 'site:consumerreports.org OR site:goodhousekeeping.com',
            'fashion': 'site:whowhatwear.com OR site:vogue.com'
        }
        
        return site_mappings.get(category, 'site:wirecutter.com OR site:rtings.com')
    
    def _google_custom_search(self, query):
        """Perform Google Custom Search with caching and rate limiting."""
        if query in self.search_cache:
            print(f"Using cached results for: {query}")
            return self.search_cache[query]
        
        current_time = time.time()
        time_since_last_search = current_time - self.last_search_time
        if time_since_last_search < 2:
            wait_time = 2 - time_since_last_search
            time.sleep(wait_time)
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.config.GOOGLE_SEARCH_API_KEY,
                'cx': self.config.GOOGLE_SEARCH_ENGINE_ID,
                'q': query,
                'num': 5
            }
            
            print(f"Searching Google for: {query}")
            response = requests.get(url, params=params)
            response.raise_for_status()
            result = response.json()
            
            items = result.get('items', [])
            self.search_cache[query] = items
            self.last_search_time = time.time()
            
            print(f"Found {len(items)} results")
            return items
        except Exception as e:
            print(f"Google Search Error: {e}")
            return []
    
        return products[:5]
    
    def _extract_products_from_results(self, search_results, original_query):
        """Extract product recommendations from search results, prioritizing full article scraping."""
        products = []
        
        # Try to scrape the top 2 results fully
        for result in search_results[:2]:
            link = result.get('link', '')
            if link:
                print(f"Scraping full article: {link}")
                scraped_products = self.article_scraper.scrape_and_extract(link, original_query)
                if scraped_products:
                    products.extend(scraped_products)
        
        # If scraping failed or returned few results, fall back to snippet extraction
        if len(products) < 3:
            print("Falling back to snippet extraction for more results...")
            for result in search_results[:3]:
                # Skip if we already scraped this link successfully
                if any(p.get('source_url') == result.get('link') for p in products):
                    continue
                    
                title = result.get('title', '')
                snippet = result.get('snippet', '')
                link = result.get('link', '')
                
                product_info = self._extract_product_info_with_gemini(title, snippet, link, original_query)
                if product_info:
                    products.extend(product_info)
        
        # Deduplicate by name (simple fuzzy match or exact match)
        unique_products = []
        seen_names = set()
        for p in products:
            name = p.get('name', '').lower()
            # Simple check to avoid exact duplicates
            if name not in seen_names:
                seen_names.add(name)
                unique_products.append(p)
        
        # Update conversation manager with found products
        self.conversation_manager.current_context["last_products"] = unique_products[:5]
        
        return unique_products[:5]
    
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

        if self.use_local:
            # Use local LLM
            result = self.llm.generate(prompt)
        else:
            # Use Gemini API
            result = self._call_gemini_api(prompt)
        
        if result:
            try:
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
            return None

    def _generate_response(self, user_query, products):
        """Generate personalized recommendation using Gemini."""
        if not products:
            return "I couldn't find any expert recommendations. Try being more specific!"
        
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
        
        context = ""
        prompt = f"""You are a helpful product recommendation assistant. 
        
User asked: "{user_query}"
{context}

Here are expert-recommended products found:
{product_list_str}

Create a natural, conversational response recommending these products. 
- Do NOT just list them 1-5. Group them logically if possible (e.g., "Best Overall", "Best Budget", "Premium Choice").
- Use bolding for product names.
- Include the price in parentheses.
- Mention key pros naturally in the sentence.
- Keep it under 200 words.
- Be friendly and helpful, like the winter boots example: "For stylish winter boots, I'd recommend considering..."
"""

        if self.use_local:
            result = self.llm.generate(prompt)
        else:
            result = self._call_gemini_api(prompt)
        
        if result:
            return result
        return f"Here are the top expert recommendations:\n\n{product_list_str}"
        
    def _handle_follow_up(self, message):
        """Handle follow-up questions using conversation context."""
        # Resolve references (e.g., "the first one")
        resolved_message = self.conversation_manager.resolve_reference(message)
        
        # Get context
        context = self.conversation_manager.get_context_for_prompt()
        
        prompt = f"""
        You are a helpful product recommendation assistant.
        
        {context}
        
        User's Follow-up Question: "{resolved_message}"
        
        Answer the question based on the conversation history and products discussed.
        If the user is asking for a comparison, compare the products mentioned.
        If the user asks for a different price/feature, suggest how they might search for that (or if you know, answer it).
        
        Keep it concise and helpful.
        """
        
        try:
            if self.use_local:
                response = self.llm.generate(prompt)
            else:
                response = self._call_gemini_api(prompt)
                
            if not response:
                return "I'm having trouble generating a response. Could you try asking in a different way?"
                
            return response
        except Exception as e:
            print(f"Error generating follow-up response: {e}")
            return "I encountered an error while processing your follow-up. Please try again."

# Create Gradio interface
def create_ui():
    chatbot_instance = ProductRecommendationChatbot()
    
    # Custom theme with off-white background and light red accents
    custom_theme = gr.themes.Base(
        primary_hue=gr.themes.colors.red,
        secondary_hue=gr.themes.colors.gray,
        neutral_hue=gr.themes.colors.gray,
    ).set(
        body_background_fill='#F5F5F0',  # Off-white background
        body_background_fill_dark='#F5F5F0',
        background_fill_primary='#FFFFFF',  # White for cards
        background_fill_secondary='#E8E8E8',  # Light gray for chat history
        button_primary_background_fill='#E57373',  # Light red
        button_primary_background_fill_hover='#EF5350',  # Slightly darker red on hover
        button_primary_text_color='#FFFFFF',  # White text on buttons
        body_text_color='#2C2C2C',  # Dark gray text
        body_text_color_subdued='#4A4A4A',  # Slightly lighter gray for secondary text
        block_label_text_color='#2C2C2C',  # Dark gray for labels
        block_title_text_color='#2C2C2C',  # Dark gray for titles
        input_background_fill='#FFFFFF',  # White input boxes
        panel_background_fill='#E8E8E8',  # Light gray for chat panel
    )
    
    with gr.Blocks(
        title="Product Recommendation Assistant",
        theme=custom_theme,
        css="""
        /* Target custom chatbot class */
        .light-chatbot {
            background-color: #E8E8E8 !important;
            background: #E8E8E8 !important;
        }
        
        .light-chatbot, 
        .light-chatbot *, 
        .light-chatbot > div, 
        .light-chatbot > div > div,
        .light-chatbot > div > div > div {
            background-color: #E8E8E8 !important;
            background: #E8E8E8 !important;
        }
        
        /* Force light background on chatbot - nuclear option */
        .chatbot, 
        .chatbot *, 
        .chatbot > div, 
        .chatbot > div > div,
        .chatbot > div > div > div,
        .chatbot .wrap, 
        .chatbot .message-wrap,
        .chatbot .overflow-y-auto,
        .chatbot .h-full,
        .chatbot .flex,
        .chatbot .flex-col,
        div[data-testid="chatbot"],
        div[data-testid="chatbot"] *,
        .chatbot .scroll-hide {
            background-color: #E8E8E8 !important;
            background: #E8E8E8 !important;
        }
        
        /* Message bubbles - override background */
        .chatbot .message, .chatbot .bot, .chatbot .user,
        .light-chatbot .message, .light-chatbot .bot, .light-chatbot .user {
            background-color: #FFFFFF !important;
            background: #FFFFFF !important;
            color: #2C2C2C !important;
        }
        
        /* User messages - light pink */
        .chatbot .user, .light-chatbot .user {
            background-color: #F5E6E6 !important;
            background: #F5E6E6 !important;
        }
        
        /* All text elements */
        *, p, span, div, label, h1, h2, h3, a {
            color: #2C2C2C !important;
        }
        
        /* Markdown text */
        .markdown-body, .prose, .prose * {
            color: #2C2C2C !important;
        }
        
        /* Input fields */
        input, textarea, .input-text {
            background-color: #FFFFFF !important;
            color: #2C2C2C !important;
        }
        
        /* Example buttons */
        .examples button {
            background-color: #FFFFFF !important;
            color: #2C2C2C !important;
            border: 1px solid #CCCCCC !important;
        }
        
        /* Labels */
        .label-wrap label {
            color: #2C2C2C !important;
        }
        """
    ) as demo:
        gr.Markdown(
            """
            # 🛍️ Product Recommendation Assistant
            
            I search expert reviews from trusted sources to find the best products for you:
            
            - **Electronics**: Wirecutter, RTINGS
            - **Home Goods**: Consumer Reports, Good Housekeeping
            - **Fashion**: Who What Wear, Vogue
            
            Ask me about any product!
            """
        )
        
        chatbot = gr.Chatbot(
            height=500,
            label="Chat History",
            show_label=True,
            avatar_images=(None, None),
            elem_classes="light-chatbot"
        )
        
        with gr.Row():
            msg = gr.Textbox(
                placeholder="Ask me about any product...",
                show_label=False,
                scale=4
            )
            submit = gr.Button("Send", scale=1, variant="primary")
        
        gr.Examples(
            examples=[
                "Stylish winter boots",
                "Best wireless headphones",
                "Best vacuum cleaner"
            ],
            inputs=msg
        )
        
        def respond(message, chat_history):
            if not message.strip():
                return chat_history, ""
            
            bot_message = chatbot_instance.chat(message, chat_history)
            chat_history.append((message, bot_message))
            return chat_history, ""
        
        msg.submit(respond, [msg, chatbot], [chatbot, msg])
        submit.click(respond, [msg, chatbot], [chatbot, msg])
    
    return demo

if __name__ == "__main__":
    demo = create_ui()
    demo.launch(share=False, server_name="127.0.0.1", server_port=7861)
