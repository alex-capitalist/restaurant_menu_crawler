"""
Integration tests for main workflow components
"""
import pytest
from unittest.mock import Mock, patch
from src.main import should_escalate, map_type_label
from src.models import MenuItem, RestaurantResult, CrawlTask, LinkInfo


class TestMainWorkflow:
    """Test main workflow functions"""
    
    def test_should_escalate_no_candidates(self):
        """should_escalate should return True when no candidates provided"""
        assert should_escalate([]) is True
        assert should_escalate(None) is True
    
    def test_should_escalate_low_confidence(self):
        """should_escalate should return True when max confidence is below threshold"""
        candidates = [
            ("url1", "text1", "type1", "label1", "format1", ["en"], 0.3),
            ("url2", "text2", "type2", "label2", "format2", ["de"], 0.4)
        ]
        assert should_escalate(candidates, min_conf=0.5) is True
    
    def test_map_type_label(self):
        """map_type_label should map type codes to labels"""
        menutypes = {
            "oct_menu": "Menu",
            "wine_menu": "Wine List"
        }
        
        assert map_type_label("oct_menu", menutypes) == "Menu"
        assert map_type_label("wine_menu", menutypes) == "Wine List"
        assert map_type_label("unknown", menutypes) == "unknown"


class TestRestaurantResultWorkflow:
    """Test RestaurantResult workflow integration"""
    
    def test_restaurant_result_creation(self):
        """Should create RestaurantResult with proper defaults"""
        result = RestaurantResult(
            name="Test Restaurant",
            url="https://example.com"
        )
        
        assert result.name == "Test Restaurant"
        assert result.url == "https://example.com"
        assert result.status == "ok"
        assert result.warnings == []
        assert result.menus == []
    
    def test_restaurant_result_with_menus(self):
        """Should handle menus correctly"""
        menu1 = MenuItem(
            link="https://example.com/menu",
            type_code="oct_menu",
            type_label="Menu",
            format="pdf"
        )
        
        result = RestaurantResult(
            name="Test Restaurant",
            url="https://example.com",
            menus=[menu1]
        )
        
        assert len(result.menus) == 1
        assert result.menus[0].type_code == "oct_menu"


class TestCrawlTaskWorkflow:
    """Test CrawlTask workflow integration"""
    
    def test_crawl_task_creation(self):
        """Should create CrawlTask with proper structure"""
        task = CrawlTask(
            url="https://example.com/menu",
            depth=2,
            call_stack=["https://example.com"]
        )
        
        assert task.url == "https://example.com/menu"
        assert task.depth == 2
        assert task.call_stack == ["https://example.com"]