# Restaurant Menu Crawler Test Suite

This directory contains unit tests for the Restaurant Menu Crawler.

## Test Structure

- `test_utils.py` - Tests for utility functions (URL normalization, domain checking, language detection)
- `test_models.py` - Tests for data models validation
- `test_link_extraction.py` - Tests for link extraction and filtering logic
- `test_heuristics.py` - Tests to ensure extracted links don't contain unwanted heuristics
- `test_workflow.py` - Integration tests for main workflow components
- `conftest.py` - Pytest configuration and fixtures
- `test_runner.py` - Simple test runner script

## Running Tests

### Using pytest directly:
```bash
# Activate virtual environment
.venv\Scripts\activate

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_utils.py

# Run with verbose output
pytest tests/ -v
```

### Using the test runner:
```bash
python tests/test_runner.py
```