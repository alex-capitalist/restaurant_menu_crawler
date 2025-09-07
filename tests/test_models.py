"""
Unit tests for data models in src/models.py
"""
import pytest
from pydantic import ValidationError
from src.models import MenuItem, RestaurantResult, CrawlTask, LinkInfo


class TestMenuItem:
    """Test MenuItem model validation and behavior"""
    
    def test_valid_menu_item(self):
        """Valid MenuItem should be created successfully"""
        menu = MenuItem(
            link="https://example.com/menu",
            type_code="oct_menu",
            type_label="Menu",
            format="pdf",
            languages=["en", "de"],
            confidence=0.8
        )
        assert menu.link == "https://example.com/menu"
        assert menu.type_code == "oct_menu"
        assert menu.confidence == 0.8
        assert menu.languages == ["en", "de"]
    
    def test_menu_item_defaults(self):
        """MenuItem should have correct defaults"""
        menu = MenuItem(
            link="https://example.com/menu",
            type_code="oct_menu",
            type_label="Menu",
            format="pdf"
        )
        assert menu.languages == []
        assert menu.confidence == 0.0
        assert menu.button_text is None


class TestRestaurantResult:
    """Test RestaurantResult model validation and behavior"""
    
    def test_valid_restaurant_result(self):
        """Valid RestaurantResult should be created successfully"""
        result = RestaurantResult(
            name="Test Restaurant",
            url="https://example.com"
        )
        assert result.name == "Test Restaurant"
        assert result.url == "https://example.com"
        assert result.status == "ok"
        assert result.warnings == []
        assert result.menus == []


class TestCrawlTask:
    """Test CrawlTask model validation and behavior"""
    
    def test_valid_crawl_task(self):
        """Valid CrawlTask should be created successfully"""
        task = CrawlTask(
            url="https://example.com/menu",
            depth=2
        )
        assert task.url == "https://example.com/menu"
        assert task.depth == 2
        assert task.call_stack == []


class TestLinkInfo:
    """Test LinkInfo model validation and behavior"""
    
    def test_valid_link_info(self):
        """Valid LinkInfo should be created successfully"""
        link = LinkInfo(
            url="https://example.com/menu",
            text="Menu"
        )
        assert link.url == "https://example.com/menu"
        assert link.text == "Menu"
    
    def test_link_info_default_text(self):
        """LinkInfo should have empty text by default"""
        link = LinkInfo(url="https://example.com/menu")
        assert link.text == ""