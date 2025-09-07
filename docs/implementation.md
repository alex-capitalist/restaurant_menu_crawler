# Implementation Documentation: Restaurant Menu Extraction System

**Version:** 1.0  
**Date:** September 3, 2025  

---

## 1. What Was Built

This document describes the actual implementation of the restaurant menu extraction system, including what works, what doesn't, and how it differs from the original PRD.

---

## 2. System Architecture

### 2.1 Core Components
- **SiteCrawler**: Main orchestrator using Playwright for browser automation
- **LinkExtractor**: Heuristic-based link discovery from DOM elements
- **LinkNoiseFilter**: Two-stage filtering (patterns + AI classifier)
- **PageParserFactory**: Route pages to appropriate parsers
  - **WebPageParser**: Standard HTML page parsing with AI classification
  - **PDFPageParser**: PDF text extraction and classification
  - **ImagePageParser**: OCR-based parsing (not implemented)
  - **CustomPageParser**: Hardcoded solutions for complex sites
- **MenuClassifier**: AI-powered menu classification
- **NoiseClassifier**: AI-powered link filtering

### 2.2 Data Flow
```
┌─────────────────┐     ┌──────────────┐      ┌─────────────────┐
│ Restaurant URL  │───▶ │   Crawler    │───▶ │ Link Extraction │
└─────────────────┘     └──────────────┘      └─────────────────┘
                                                        │
                                                        ▼
                                              ┌─────────────────┐
                                              │ Heuristic Filter│
                                              └─────────────────┘
                                                        │
                                                        ▼
                                              ┌─────────────────────┐
                                              │ Link Classification │
                                              │ (Noise Filter)      │
                                              └─────────────────────┘
                                                        │
                                                        ▼
                                              ┌─────────────────┐
                                              │  Page Parsing   │
                                              └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────────┐
│ JSON Output     │◀───│ Menu Classification │
└─────────────────┘    └─────────────────────┘
```

---

## 3. Implemented Features

### 3.1 ✅ Working Features

#### Website Crawling
- **Playwright Integration**: Full browser automation with headless Chrome
- **Configurable Depth**: Crawling depth controlled via `MAX_CRAWL_DEPTH` (default: 3)
- **Link Extraction**: Extracts links from `<a href>`, `onclick`, `data-href`, `data-url`
- **Domain Filtering**: Only processes same-domain links
- **Duplicate Prevention**: Tracks visited and queued URLs

#### Cookie Banner Handling
- **Detection**: Finds cookie accept buttons using text patterns
- **Multi-language Support**: Detects buttons in DE/EN/FR/IT
- **Auto-click**: Attempts to click accept buttons when found
- **Text Recording**: Captures accept button text for output

#### Menu Classification
- **AI-Powered**: Uses local LLM for menu type classification
- **Format Detection**: Identifies PDF, integrated, viewer formats
- **Language Detection**: Uses `langdetect` + heuristics for DE/EN/FR/IT
- **Confidence Scoring**: Provides confidence levels for classifications
- **Type Mapping**: Maps to predefined menu types (lunch, dinner, wine, etc.)

#### Web & PDF Processing
- **Web Pages**: Standard HTML parsing with text extraction
- **PDF Processing**: Extracts text from first page using PyMuPDF
- **Text Limitation**: Caps extracted text to 3.5K characters to fit small model context (with prompt)
- **Size Limits**: Configurable download limits (default: 4MB to cover big files)
- **Content-Disposition**: Captures PDF filename from headers
- **Error Handling**: Graceful handling of corrupted/unreadable PDFs

#### Output Generation
- **Structured JSON**: Per-restaurant results with menu arrays
- **Status Tracking**: Success/failure status for each restaurant
- **Error Reporting**: Detailed error messages and warnings to console
- **Metadata**: Includes confidence scores, languages, formats

### 3.2 ❌ Missing Features (from PRD)

#### Agentic Fallback System
- **Planned**: AI fallback when heuristics fail
- **Reality**: AI is used for classification throughout, not as fallback
- **Impact**: No intelligent retry or alternative discovery methods

#### Advanced Navigation
- **SPA Detection**: No detection of Single Page Application navigation
- **Sitemap Crawling**: Code exists but is commented out/disabled

#### Future Processing
- **Image OCR**: Image menus marked as "not implemented"
- **PDF Button Text**: No extraction of download button text
- **Advanced Format Detection**: Limited to basic PDF/HTML/viewer detection

---

## 4. Configuration

### 4.1 Environment Variables
```bash
MAX_CRAWL_DEPTH=3                             # Crawling depth
NOISE_CONFIDENCE_THRESHOLD=0.3                # Noise filter threshold
MENU_ITEM_CLASSIFIER_CONFIDENCE_THRESHOLD=0.7 # Menu classification threshold
OPENAI_API_BASE=http://localhost:1234/v1      # LLM server URL
OPENAI_MODEL=gpt-oss-20b                      # Model name
OPENAI_API_KEY=sk-noauth                      # API key (can be any for LLM Studio)
MAX_PDF_BYTES=1000000                         # PDF download limit
MAX_PDF_TEXT_CHARS=3500                       # Text extraction limit
```

### 4.2 Input Files
- `input/restaurants.json`: Restaurant name → URL mapping
- `input/menutypes.json`: Menu type codes and labels
- `input/menuformats.json`: Format definitions

### 4.3 Output Format
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

---

## 5. Performance Metrics

### 5.1 Current Performance
- **Test Dataset**: 14 restaurants
- **Total Time**: ~540 seconds (38.6s per restaurant)
- **Success Rate**: ~85% (12/14 restaurants with menus found)
- **Menu Detection**: Average 2-3 menus per successful restaurant

### 5.2 Optimization Targets
- **Target Time**: <135 seconds total (<9.6s per restaurant)
- **Optimization Strategies**:
  - Replace LLM with fast ML models
  - Add more heuristics to reduce AI calls
  - Implement caching for unchanged sites
  - Add parallel processing

---

## 6. Technical Implementation Details

### 6.1 Crawling Strategy
- **Breadth-First**: Processes pages level by level
- **Depth Limiting**: Stops at configured maximum depth
- **Smart Filtering**: Excludes child pages when specific menus found
- **Error Recovery**: Continues processing despite individual page failures

### 6.2 AI Integration
- **Local LLM**: Uses configurable local server (default: localhost:1234)
- **Batch Processing**: Processes links in batches of 20 (**to make sure the links and the prompt fit to the default small model context**)
- **Prompt Engineering**: Structured prompts for consistent JSON output

### 6.3 Special Cases
- **Custom Parsers**: Hardcoded solutions for problematic sites (e.g., Gamper Restaurant)
- **PDF Handling**: Specialized parser for PDF documents
- **Image Detection**: Basic detection but no OCR processing

---

## 7. Known Limitations

### 7.1 Technical Limitations
- **Image Menus**: No OCR processing for image-based menus
- **Rate Limiting**: No built-in rate limiting or respectful crawling

### 7.2 Accuracy Limitations
- **False Positives**: May classify non-menu pages as menus
- **Language Detection**: Limited to 4 languages (DE/EN/FR/IT)
- **Format Detection**: Basic format classification without deep analysis
- **Confidence Scoring**: Simple confidence calculation

### 7.3 Scalability Limitations
- **Sequential Processing**: No parallel restaurant processing
- **Memory Usage**: Loads full pages into memory
- **No Caching**: Re-processes unchanged sites
- **Single Machine**: No distributed processing support

---

## 8. Future Improvements

- Integrate with database storage
- Add more sophisticated heuristics to reduce AI calls
- Improve error handling and retry logic
- Add progress indicators and better logging
- Train fast ML models for links classification and replace the LLM links classificaiton calls
- Implement caching for unchanged sites
- Add image OCR support for image menus
- Add distributed processing support
- Implement web-based review interface
- Add automated scheduling and updates
- Implement parallel processing for multiple restaurants

---

## 9. Deployment & Usage

### 9.1 Docker Deployment
```bash
docker build -t menu-extractor .
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output menu-extractor
```

### 9.2 Local Development (Windows)

#### 1. Setting up Virtual Environment
```cmd
python -m venv .venv
```

#### 2. Installing Dependencies
```cmd
.venv\Scripts\activate
pip install -r requirements.txt
playwright install --with-deps
```

#### 3. Running the Application
Given that input data is in `./input` and output data will be placed to `./output` folders.

```cmd
.venv\Scripts\activate
python -m src.main 
```

### 9.3 LLM Server Setup

#### Download and Install LM Studio
1. Download LM Studio from: https://lmstudio.ai/
2. Install and launch the application
3. On the "Chats" tab pick `OpenAI's gpt-oss 20B MXFP4` (or similar, but the model name should be reflected in the respective .env parameters).

#### Starting the Local Server
1. In LM Studio, go to the "Developer" tab
3. Click "Start Server" 
4. The server will start on `http://localhost:1234` (default port)
5. Verify the server is running by visiting `http://localhost:1234/v1/models` in your browser

#### Configuration
- The default configuration works with the system's environment variables
- No API key required for local server (use `sk-noauth` as placeholder)

---

## 10. Conclusion

The implemented system successfully extracts menu information from restaurant websites using a hybrid approach of heuristics and AI classification. While it doesn't include all planned features (particularly the agentic fallback system), it provides a solid foundation for automated menu extraction with room for future enhancements.

The system is production-ready for small to medium-scale deployments but would benefit from performance optimizations and additional features for large-scale processing.
