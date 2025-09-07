"""
Pytest configuration and fixtures for Restaurant Menu Crawler tests
"""
import pytest
import os
import sys
from unittest.mock import Mock, patch

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def sample_menutypes():
    """Sample menu types for testing"""
    return {
        "oct_menu": "Menu",
        "wine_menu": "Wine List",
        "dessert_menu": "Desserts",
        "breakfast_menu": "Breakfast",
        "lunch_menu": "Lunch",
        "dinner_menu": "Dinner"
    }


@pytest.fixture
def sample_links():
    """Sample links for testing"""
    return [
        LinkInfo(url="https://example.com/menu", text="Menu"),
        LinkInfo(url="https://example.com/about", text="About us"),
        LinkInfo(url="https://example.com/contact", text="Contact"),
        LinkInfo(url="https://example.com/wine", text="Wine List"),
        LinkInfo(url="https://example.com/reservation", text="Reservation")
    ]


@pytest.fixture
def sample_menu_item():
    """Sample menu item for testing"""
    return MenuItem(
        link="https://example.com/menu",
        type_code="oct_menu",
        type_label="Menu",
        format="pdf",
        languages=["en", "de"],
        confidence=0.8,
        notes="Found in navigation"
    )


@pytest.fixture
def sample_restaurant_result():
    """Sample restaurant result for testing"""
    return RestaurantResult(
        name="Test Restaurant",
        url="https://example.com",
        status="ok",
        warnings=[],
        menus=[]
    )


@pytest.fixture
def mock_llm():
    """Mock LLM for testing"""
    mock = Mock()
    mock.invoke.return_value = Mock(content='{"menus": []}')
    return mock


@pytest.fixture
def mock_page():
    """Mock Playwright page for testing"""
    mock = Mock()
    mock.content.return_value = "<html><body>Test content</body></html>"
    mock.title.return_value = "Test Page"
    mock.eval_on_selector_all.return_value = []
    return mock


# Import models for fixtures
from src.models import LinkInfo, MenuItem, RestaurantResult
