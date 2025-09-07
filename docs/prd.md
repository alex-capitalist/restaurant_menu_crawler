# Product Requirements Document: Restaurant Menu Extraction System

**Version:** 1.0  
**Date:** September 3, 2025  
**Owner:** Engineering (Search & Data)  

---

## 1. Executive Summary

This document outlines the requirements for an automated system that extracts structured menu information from restaurant websites. The system will crawl restaurant sites, identify menu pages, classify menu types and formats, and output structured data for further processing.

---

## 2. Problem Statement

Restaurant menu data is scattered across thousands of websites in various formats (PDF, HTML, images). Manual extraction is time-consuming and doesn't scale. We need an automated solution that can:

- Discover menu pages on restaurant websites
- Classify menu types (lunch, dinner, wine, etc.)
- Identify formats (PDF, integrated HTML, viewer)
- Extract language information
- Handle cookie banners and navigation challenges

---

## 3. Goals & Success Criteria

### Primary Goals
- **Automated Discovery**: Automatically find menu pages on restaurant websites
- **Structured Output**: Generate consistent JSON data with menu information
- **Multi-format Support**: Handle PDF, HTML, and embedded menu formats
- **Language Detection**: Identify menu languages (DE, EN, FR, IT)
- **Scalability**: Process 1000+ restaurants efficiently

### Success Criteria
- Extract at least one valid menu from 80% of restaurant websites
- Achieve 90%+ accuracy in menu type classification
- Process 100 restaurants in under 2 hours
- Handle cookie banners on 95% of sites
- Support PDF, HTML, and embedded menu formats

---

## 4. Functional Requirements

### 4.1 Website Crawling
- Crawl restaurant websites up to configurable depth (default: 3 levels)
- Extract internal links from DOM elements (`<a>`, `onclick`, `data-href`)
- Handle cookie banners by detecting and clicking accept buttons
- Avoid infinite loops and duplicate page visits

### 4.2 Menu Detection & Processing
- Identify pages containing menu content using AI classification
- Classify menu types from predefined list (lunch, dinner, wine, etc.)
- Detect menu format (PDF, integrated HTML, embedded viewer)
- Extract text from PDF menus (first page only)
- Detect language information (DE, EN, FR, IT)

### 4.3 Output Generation
- Generate structured JSON output per restaurant
- Include restaurant metadata, discovered menus, and confidence scores
- Record cookie banner accept button text when found
- Include error messages and warnings for failed extractions

---

## 5. Non-Functional Requirements

### 5.1 Performance
- Process 100 restaurants in under 2 hours
- Handle timeouts gracefully (15s page load, 60s network idle)
- Limit PDF downloads to 1MB per file
- Cap text extraction to 3500 characters per page

### 5.2 Reliability & Usability
- Continue processing if individual sites fail
- Support configuration via environment variables
- Provide clear command-line interface with console output
- Generate human-readable JSON output with error reporting

---

## 6. Technical Constraints

### 6.1 Data & Security
- Input: JSON file with restaurant name → URL mapping
- Output: Single JSON file with all results
- Support multilingual content (DE, EN, FR, IT)
- No authentication, CAPTCHA, or aggressive crawling

---

## 7. Out of Scope

### 7.1 Explicitly Excluded
- CAPTCHA solving, login authentication, or OCR processing
- Database persistence (file output only)
- Real-time scheduling or complex SPA handling

### 7.2 Dependencies
- LLM server (local or external) with OpenAI-compatible API
- Input files: `restaurants.json`, `menutypes.json`, `menuformats.json`
- Environment variables for LLM server configuration

---

## 8. Risks & Mitigations

### 8.1 Technical Risks
- **LLM server unavailability**: Graceful degradation with heuristics-only mode
- **Complex SPA navigation**: Focus on traditional HTML sites, log SPA detection
- **PDF processing failures**: Skip problematic PDFs, log errors

### 8.2 Performance & Quality Risks
- **Slow website response times**: Configurable timeouts, size limits
- **False positive menu detection**: Confidence thresholds, manual review process
- **Language detection errors**: Fallback to heuristics, manual correction
