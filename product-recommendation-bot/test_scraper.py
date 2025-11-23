import unittest
from unittest.mock import MagicMock, patch
from article_scraper import ArticleScraper

class TestArticleScraper(unittest.TestCase):
    def setUp(self):
        self.mock_llm = MagicMock()
        self.mock_llm.generate.return_value = '''
        [
            {
                "name": "Test Product",
                "price": "$99",
                "pros": "Good quality",
                "cons": "Expensive",
                "description": "A great test product",
                "rating": "9/10",
                "award": "Top Pick",
                "source_url": "http://test.com"
            }
        ]
        '''
        self.scraper = ArticleScraper(llm_provider=self.mock_llm)

    @patch('article_scraper.requests.get')
    def test_fetch_article(self, mock_get):
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'<html><body><article><h1>Review</h1><p>This is a review of the Test Product.</p></article></body></html>'
        mock_get.return_value = mock_response

        # Test internal fetch
        content = self.scraper._fetch_article("http://test.com")
        self.assertIn("This is a review", content)
        self.assertNotIn("<html>", content)

    @patch('article_scraper.requests.get')
    def test_scrape_and_extract(self, mock_get):
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'<html><body><article><p>Content</p></article></body></html>'
        mock_get.return_value = mock_response

        # Test full flow
        products = self.scraper.scrape_and_extract("http://test.com", "test query")
        
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]['name'], "Test Product")
        self.mock_llm.generate.assert_called_once()

if __name__ == '__main__':
    unittest.main()
