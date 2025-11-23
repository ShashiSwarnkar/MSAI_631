import unittest
from conversation_manager import ConversationManager

class TestConversationManager(unittest.TestCase):
    def setUp(self):
        self.cm = ConversationManager()

    def test_add_message(self):
        self.cm.add_message("user", "Hello")
        self.assertEqual(len(self.cm.history), 1)
        self.assertEqual(self.cm.history[0]['text'], "Hello")

    def test_is_follow_up(self):
        self.cm.add_message("user", "Best laptop")
        self.assertTrue(self.cm.is_follow_up("What about the price?"))
        self.assertTrue(self.cm.is_follow_up("cheaper one"))
        self.assertFalse(self.cm.is_follow_up("Best coffee maker"))

    def test_resolve_reference(self):
        products = [{"name": "Product A"}, {"name": "Product B"}]
        self.cm.add_message("user", "Show me products")
        self.cm.add_message("assistant", "Here they are", products=products)
        
        resolved = self.cm.resolve_reference("tell me about the first one")
        self.assertIn("Product A", resolved)
        
        resolved = self.cm.resolve_reference("compare the second one")
        self.assertIn("Product B", resolved)

    def test_context_formatting(self):
        self.cm.add_message("user", "Hi")
        self.cm.add_message("assistant", "Hello")
        context = self.cm.get_context_for_prompt()
        self.assertIn("User: Hi", context)
        self.assertIn("Assistant: Hello", context)

if __name__ == '__main__':
    unittest.main()
