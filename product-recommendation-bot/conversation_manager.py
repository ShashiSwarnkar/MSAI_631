"""
Conversation Manager for Product Recommendation Bot
Handles conversation history, context tracking, and follow-up question detection.
"""
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationManager:
    def __init__(self, llm_provider=None):
        """
        Initialize Conversation Manager.
        
        Args:
            llm_provider: Function or object with .generate() method for intelligent analysis.
        """
        self.llm_provider = llm_provider
        self.history = []  # List of message dicts
        self.user_profile = {
            "budget_range": {"min": None, "max": None},
            "preferred_brands": [],
            "disliked_brands": [],
            "priorities": [],  # e.g., "battery life", "camera"
            "last_category": None
        }
        self.current_context = {
            "last_products": [],  # Products mentioned in the last assistant response
            "active_filters": {}
        }

    def add_message(self, role, text, products=None):
        """
        Add a message to the history.
        
        Args:
            role: 'user' or 'assistant'
            text: Message content
            products: List of products (for assistant messages)
        """
        message = {
            "role": role,
            "text": text,
            "timestamp": datetime.now().isoformat()
        }
        
        if products:
            message["products"] = products
            self.current_context["last_products"] = products
            
        self.history.append(message)
        
        # If user message, update profile (simple heuristic for now)
        if role == 'user':
            self._update_profile_heuristics(text)

    def get_history(self, limit=None):
        """Get recent conversation history."""
        if limit:
            return self.history[-limit:]
        return self.history

    def get_context_for_prompt(self):
        """
        Format history and context for LLM prompt.
        Returns a string representation of the conversation.
        """
        context_str = "Conversation History:\n"
        
        # Include last 5 messages
        recent_history = self.history[-5:]
        for msg in recent_history:
            role = "User" if msg['role'] == 'user' else "Assistant"
            context_str += f"{role}: {msg['text']}\n"
            
        # Add user profile summary if available
        profile_str = []
        if self.user_profile['budget_range']['max']:
            profile_str.append(f"Budget: Under ${self.user_profile['budget_range']['max']}")
        if self.user_profile['preferred_brands']:
            profile_str.append(f"Likes: {', '.join(self.user_profile['preferred_brands'])}")
        
        if profile_str:
            context_str += "\nUser Context: " + "; ".join(profile_str)
            
        return context_str

    def is_follow_up(self, message):
        """
        Determine if the message is a follow-up to the previous conversation.
        Returns True if it seems to reference previous context.
        """
        if not self.history:
            return False
            
        # Simple heuristics for follow-ups
        follow_up_keywords = [
            'it', 'they', 'them', 'that', 'those', 'one', 'first', 'second', 'third',
            'cheaper', 'expensive', 'better', 'worse', 'compare', 'difference',
            'what about', 'how about', 'and', 'but', 'why', 'tell me', 'more about',
            'find me', 'search for', 'looking for', 'recommend', 'show me'
        ]
        
        msg_lower = message.lower()
        
        # Check for keywords
        for keyword in follow_up_keywords:
            if f" {keyword} " in f" {msg_lower} " or msg_lower.startswith(keyword):
                return True
                
        # If message is very short, likely a follow-up (e.g., "under 500")
        # But exclude common search starters
        if len(message.split()) < 5:
            starters = ['best', 'top', 'cheap', 'affordable', 'review']
            if not any(msg_lower.startswith(s) for s in starters):
                return True
            
        return False

    def _update_profile_heuristics(self, text):
        """Update user profile based on simple text analysis."""
        text_lower = text.lower()
        
        # Extract budget (simple regex-like check)
        import re
        price_match = re.search(r'under \$?(\d+)', text_lower)
        if price_match:
            self.user_profile['budget_range']['max'] = int(price_match.group(1))
            
        # Extract brands (would need a known brand list or NER for robust extraction)
        # For now, relying on the main app's extraction logic which will be passed in
        
        # Update category if detected
        # (This logic is currently in the main app, will be integrated later)

    def resolve_reference(self, message):
        """
        Resolve references like "the first one" or "Sony" to specific product names.
        """
        if not self.current_context["last_products"]:
            return message
            
        msg_lower = message.lower()
        products = self.current_context["last_products"]
        
        # 1. Check for ordinal references
        ordinals = {
            "first": 0, "1st": 0,
            "second": 1, "2nd": 1,
            "third": 2, "3rd": 2,
            "fourth": 3, "4th": 3,
            "fifth": 4, "5th": 4
        }
        
        for word, idx in ordinals.items():
            if word in msg_lower and idx < len(products):
                product_name = products[idx].get('name', 'Product')
                return f"{message} (referring to {product_name})"
                
        # 2. Check for product name references (fuzzy match)
        for product in products:
            name = product.get('name', '').lower()
            # If a significant part of the product name is in the message
            # e.g. "Sony" in "Tell me about the Sony one"
            # We check if any word in the product name (longer than 3 chars) is in the message
            name_parts = [p for p in name.split() if len(p) > 3]
            for part in name_parts:
                if part in msg_lower:
                    # Found a match, but check if it's already fully specified
                    if name not in msg_lower:
                         return f"{message} (referring to {product.get('name')})"
                         
        return message

if __name__ == "__main__":
    # Simple test
    cm = ConversationManager()
    cm.add_message("user", "Best headphones under $200")
    cm.add_message("assistant", "Here are some options...", products=[{"name": "Sony WH-1000XM4"}, {"name": "Bose QC45"}])
    
    print("History:", cm.get_history())
    print("Is follow-up 'what about the first one?':", cm.is_follow_up("what about the first one?"))
    print("Resolved:", cm.resolve_reference("tell me more about the first one"))
