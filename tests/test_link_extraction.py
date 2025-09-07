"""
Unit tests for link extraction and filtering functionality
"""
import pytest
from unittest.mock import Mock, patch
from src.link_extractor import LinkExtractor, LinkNoiseFilter
from src.models import LinkInfo, CrawlTask


class TestLinkExtractor:
    """Test LinkExtractor functionality"""
    
    def test_init_with_max_depth(self):
        """LinkExtractor should initialize with correct max_depth"""
        extractor = LinkExtractor(max_depth=5)
        assert extractor.max_depth == 5
    
    def test_extract_exceeds_max_depth(self):
        """extract should return empty list when depth exceeds max_depth"""
        extractor = LinkExtractor(max_depth=2)
        task = CrawlTask(url="https://example.com", depth=3)
        mock_page = Mock()
        
        result = extractor.extract(mock_page, task)
        assert result == []
    
    def test_extract_pdf_links_from_page(self):
        """Should extract PDF links from page content"""
        from bs4 import BeautifulSoup
        
        extractor = LinkExtractor()
        html = """
        <html>
            <body>
                <a href="menu.pdf">PDF Menu</a>
                <embed src="viewer.pdf" type="application/pdf">
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        
        result = extractor._extract_pdf_links_from_page(soup, "https://example.com/")
        
        # Should find PDF links
        urls = [link.url for link in result]
        assert "https://example.com/menu.pdf" in urls
        assert "https://example.com/viewer.pdf" in urls


class TestLinkNoiseFilter:
    """Test LinkNoiseFilter functionality"""
    
    def test_init(self):
        """LinkNoiseFilter should initialize correctly"""
        filter_instance = LinkNoiseFilter()
        assert hasattr(filter_instance, '_noise_classifier')
    
    def test_filter_handles_empty_list(self):
        """Should handle empty link list gracefully"""
        filter_instance = LinkNoiseFilter()
        
        with patch.object(filter_instance._noise_classifier, 'classify', return_value=[]):
            result = filter_instance.filter([])
        
        assert result == []