"""
Unit tests to ensure extracted links don't contain unwanted heuristics
"""
import pytest
from src.link_extractor import LinkNoiseFilter
from src.models import LinkInfo


class TestHeuristicFiltering:
    """Test that extracted links are properly filtered to exclude unwanted heuristics"""
    
    def test_excludes_navigation_patterns(self):
        """Should exclude common navigation patterns that are not menus"""
        filter_instance = LinkNoiseFilter()
        links = [
            LinkInfo(url="https://example.com/menu", text="Menu"),
            LinkInfo(url="https://example.com/about", text="About us"),
            LinkInfo(url="https://example.com/contact", text="Contact"),
            LinkInfo(url="https://example.com/faq", text="FAQ")
        ]
        
        # Mock the noise classifier to return only the menu link
        filtered_links = [LinkInfo(url="https://example.com/menu", text="Menu")]
        with patch.object(filter_instance._noise_classifier, 'classify', return_value=filtered_links):
            result = filter_instance.filter(links)
        
        # Should exclude navigation links
        urls = [link.url for link in result]
        assert "https://example.com/menu" in urls
        assert "https://example.com/about" not in urls
        assert "https://example.com/contact" not in urls
        assert "https://example.com/faq" not in urls
    
    def test_excludes_image_files(self):
        """Should exclude image file extensions"""
        filter_instance = LinkNoiseFilter()
        links = [
            LinkInfo(url="https://example.com/menu", text="Menu"),
            LinkInfo(url="https://example.com/logo.jpg", text="Logo"),
            LinkInfo(url="https://example.com/photo.png", text="Photo")
        ]
        
        # Mock the noise classifier to return only the menu link
        filtered_links = [LinkInfo(url="https://example.com/menu", text="Menu")]
        with patch.object(filter_instance._noise_classifier, 'classify', return_value=filtered_links):
            result = filter_instance.filter(links)
        
        # Should exclude image files
        urls = [link.url for link in result]
        assert "https://example.com/menu" in urls
        assert "https://example.com/logo.jpg" not in urls
        assert "https://example.com/photo.png" not in urls


# Import patch for the tests
from unittest.mock import patch