"""
Unit tests for utility functions in src/utils.py
"""
import pytest
from src.utils import (
    normalize_url, 
    is_same_domain, 
    canonicalize_language, 
    de_duplicate, 
    deduplicate_by_key,
    guess_languages_from_text
)


class TestNormalizeUrl:
    """Test URL normalization functionality"""
    
    def test_absolute_url_unchanged(self):
        """Absolute URLs should remain unchanged"""
        base = "https://example.com/page"
        url = "https://other.com/path"
        result = normalize_url(base, url)
        assert result == "https://other.com/path"
    
    def test_relative_url_normalized(self):
        """Relative URLs should be normalized against base"""
        base = "https://example.com/page/"
        url = "menu.html"
        result = normalize_url(base, url)
        assert result == "https://example.com/page/menu.html"


class TestIsSameDomain:
    """Test domain matching functionality"""
    
    def test_exact_domain_match(self):
        """Exact domain matches should return True"""
        root = "https://example.com/page"
        url = "https://example.com/menu"
        assert is_same_domain(root, url) is True
    
    def test_subdomain_match(self):
        """Subdomain matches should return True"""
        root = "https://example.com"
        url = "https://www.example.com/menu"
        assert is_same_domain(root, url) is True
    
    def test_different_domain(self):
        """Different domains should return False"""
        root = "https://example.com"
        url = "https://other.com/menu"
        assert is_same_domain(root, url) is False


class TestCanonicalizeLanguage:
    """Test language canonicalization functionality"""
    
    def test_remove_language_segments(self):
        """Language segments in paths should be removed"""
        url = "https://example.com/de/menu"
        result = canonicalize_language(url)
        assert result == "https://example.com/menu"
    
    def test_remove_trailing_slashes(self):
        """Trailing slashes should be cleaned up"""
        url = "https://example.com//"
        result = canonicalize_language(url)
        assert result == "https://example.com/"


class TestDeDuplicate:
    """Test deduplication functionality"""
    
    def test_remove_duplicates(self):
        """Duplicate items should be removed"""
        items = ["a", "b", "a", "c", "b"]
        result = de_duplicate(items)
        assert result == ["a", "b", "c"]
    
    def test_preserve_order(self):
        """First occurrence should be preserved"""
        items = ["b", "a", "c", "a", "b"]
        result = de_duplicate(items)
        assert result == ["b", "a", "c"]


class TestGuessLanguagesFromText:
    """Test language detection heuristics"""
    
    def test_german_detection(self):
        """German keywords should be detected"""
        text = "Speisekarte und Getränke"
        result = guess_languages_from_text(text)
        assert "de" in result
    
    def test_english_detection(self):
        """English keywords should be detected"""
        text = "Menu and wine selection"
        result = guess_languages_from_text(text)
        assert "en" in result
    
    def test_multiple_languages(self):
        """Multiple languages should be detected"""
        text = "Menu und carte e wine"
        result = guess_languages_from_text(text)
        assert "en" in result
        assert "de" in result
        assert "fr" in result