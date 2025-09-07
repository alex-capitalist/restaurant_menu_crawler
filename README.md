# Restaurant Menu Extraction System

## **PRE-GENERATED OUTPUT AVAILABLE**

**This repository contains pre-generated output based on the provided input data. You can find the results in the `output/` folder without needing to run the application yourself.**

If you prefer not to set up and run the system, you can directly access the extracted menu data from `output/output.json`.

---

## Documentation

For detailed information about the system, please refer to the documentation in the `/docs` folder:

- **[Task Description](docs/task.md)**: Original task requirements and deliverables
- **[Product Requirements Document](docs/prd.md)**: Complete system requirements and specifications
- **[Implementation Documentation](docs/implementation.md)**: Technical details, architecture, and current implementation status
- **[Solution Analysis](docs/options.md)**: Comparison of different approaches and performance analysis
- **[Agentic AI Documentation](docs/agentic-ai.md)**: Current AI implementation and future agentic AI plans

## Overview
An automated system that extracts structured menu information from restaurant websites using a hybrid approach combining heuristics and AI classification. The system crawls restaurant sites, identifies menu pages, classifies menu types and formats, and outputs structured JSON data.

## Key Features
- **Automated Discovery**: Automatically finds menu pages on restaurant websites
- **Multi-format Support**: Handles PDF, HTML, and embedded menu formats
- **AI-Powered Classification**: Uses local LLM for menu type and format classification
- **Cookie Banner Handling**: Automatically detects and handles cookie consent banners
- **Language Detection**: Identifies menu languages (DE, EN, FR, IT)
- **Structured Output**: Generates consistent JSON data with menu information

## System Architecture
The system uses a modular architecture with the following components:
- **SiteCrawler**: Playwright-based browser automation for website crawling
- **LinkExtractor**: Heuristic-based link discovery from DOM elements
- **NoiseClassifier**: AI-powered filtering of non-menu links
- **MenuClassifier**: AI-powered menu classification and analysis
- **PageParserFactory**: Routes pages to appropriate parsers (Web, PDF, Image)

## System Requirements

### Hardware Requirements
- **GPU**: Minimum 8GB VRAM (ideally 16GB) for LLM server
- **RAM**: Minimum 16GB (ideally 64GB) for optimal performance
  - **Mac**: Mac with 24GB RAM should **theoretically** be sufficient to run both the model and the script
- **Storage**: ~10GB for models and dependencies

### Software Requirements
- **Python**: 3.9 or higher
- **Docker**: Optional, for containerized deployment
- **Local LLM Server**: Required for AI classification (see setup instructions below)

### Tested Environment
- **Windows**: Windows 10, 16GB VRAM, 64GB RAM (validated)
- **Mac**: Mac with 24GB RAM should **theoretically** be sufficient to run both the model and the script, though this hasn't been tested

## Quick Start

### 1. Set Up Local LLM Server (Required)
1. Download and install [LM Studio](https://lmstudio.ai/)
2. Launch LM Studio and go to the "Chats" tab
3. Download `OpenAI's gpt-oss 20B MXFP4` model (or similar)
4. Go to the "Developer" tab and click "Start Server"
5. Server will run on `http://localhost:1234` (default)


### Option A: Docker (Recommended)
1. Start your local AI model server (e.g., LM Studio)
2. Run: `run-docker.bat` (Windows) or `./run-docker.sh` (Linux/Mac)
3. Check results in `output/output.json`

### Option B: Local Python Environment

#### Windows
```cmd
# Create virtual environment
python -m venv .venv

# Activate environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install --with-deps
```

#### macOS/Linux (not tested)
```bash
# Create virtual environment
python -m venv .venv

# Activate environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install --with-deps
```

### 3. Run the Application (Windows)

#### Basic Usage
```cmd
# Activate environment (if not already active)
.venv\Scripts\activate

# Run with default settings
python -m src.main
```

#### Custom Input/Output Files
```cmd
python -m src.main --input input\restaurants.json --types input\menutypes.json --formats input\menuformats.json --out output\output.json
```

## Configuration

The application can be configured via environment variables:

### Core Settings
- `MAX_CRAWL_DEPTH`: Maximum crawling depth (default: 3)
- `NOISE_CONFIDENCE_THRESHOLD`: Threshold for filtering noise links (default: 0.3)
- `MENU_ITEM_CLASSIFIER_CONFIDENCE_THRESHOLD`: Threshold for menu classification (default: 0.7)

### LLM Server Settings
- `OPENAI_API_BASE`: LLM API base URL (default: http://localhost:1234/v1)
- `OPENAI_API_KEY`: API key (default: sk-noauth for local servers)
- `OPENAI_MODEL`: Model name (default: gpt-oss-20b)

### Performance Settings
- `MAX_PDF_BYTES`: PDF download limit in bytes (default: 1000000)
- `MAX_PDF_TEXT_CHARS`: Text extraction limit (default: 3500)



## Performance Metrics

### Current Performance (Test Dataset: 14 restaurants)
- **Total Processing Time**: ~540 seconds (38.6s per restaurant)
- **Success Rate**: ~85% (12/14 restaurants with menus found)
- **Menu Detection**: Average 2-3 menus per successful restaurant
- **Memory Usage**: ~2-4GB RAM during processing

### Optimization Targets
- **Target Time**: <135 seconds total (<9.6s per restaurant)
- **Scaling Projections**:
  - 1K restaurants: ~2.7 hours (optimized) → 32 minutes (with caching)
  - 10K restaurants: ~26.8 hours (optimized) → 5.4 hours (with caching)

### Optimization Strategies
1. Replace LLM with fast ML models (Random Forest/LightGBM)
2. Add more heuristics to reduce AI calls
3. Implement caching for unchanged sites
4. Add parallel processing for multiple restaurants

## Input/Output Format

### Input Files
- `input/restaurants.json`: Restaurant name → URL mapping
- `input/menutypes.json`: Menu type codes and labels
- `input/menuformats.json`: Format definitions

### Output Format
```json
{
  "restaurants": [
    {
      "name": "restaurant_name",
      "url": "https://example.com",
      "cookie_banner_accept": "Accept All",
      "status": "ok",
      "warnings": [],
      "menus": [
        {
          "link": "https://example.com/menu",
          "type_code": "oct_menu",
          "type_label": "Menu",
          "format": "integrated",
          "languages": ["de", "en"],
          "button_text": null,
          "confidence": 0.85,
          "notes": "Classification reasoning",
          "content_disposition": null
        }
      ]
    }
  ]
}
```

## Known Limitations

### Technical Limitations
- **Image Menus**: No OCR processing for image-based menus
- **Rate Limiting**: No built-in rate limiting or respectful crawling
- **Sequential Processing**: No parallel restaurant processing
- **No Caching**: Re-processes unchanged sites

### Accuracy Limitations
- **False Positives**: May classify non-menu pages as menus
- **Language Detection**: Limited to 4 languages (DE/EN/FR/IT)
- **Format Detection**: Basic format classification without deep analysis

## Future Improvements

- Integrate with database storage
- Add more sophisticated heuristics to reduce AI calls
- Improve error handling and retry logic
- Add progress indicators and better logging
- Train fast ML models for link classification
- Implement caching for unchanged sites
- Add image OCR support for image menus
- Add distributed processing support
- Implement web-based review interface
- Add automated scheduling and updates