# Agentic AI Prototype — Restaurant Menu Extraction

**Version:** 1.0  
**Date:** September 3, 2025  
**Owner:** Engineering (Search & Data)  

---

## 1. Purpose

Demonstrate a hybrid **heuristics-first with agentic fallback** system that extracts restaurant menu information from websites into structured data. The agent (LLM via LangChain) assists when rules fail or confidence is low.

---

## 2. Goals & Non-Goals

### Goals
- Crawl each restaurant site up to **depth=3** (configurable via MAX_CRAWL_DEPTH env var, avoid blow-ups).
- Detect **cookie banner** and record the *accept* button text if shown.
- Identify **menus** (links or pages): derive
  - **menu type** (from a predefined list),
  - **format** (pdf / viewer / integrated / image),
  - **language(s)**,
  - **PDF open/download button** text where applicable.
- Output per-restaurant JSON with status, warnings, and confidence.
- **Agentic fallback**: when heuristics cannot confidently classify or find menus.

### Non-Goals (for this prototype)
- CAPTCHA solving, login-walled content.
- Complex OCR of image-only PDFs/pages.
- Scheduling/orchestration (single CLI run).
- Database persistence (file output only).

---

## 3. Approach Overview

1. **Heuristics-first crawler (Playwright, depth=3, configurable)**  
   - Wait for `networkidle`. Try to detect/click cookie banner (log accept text).  
   - Collect internal links from:
     - `<a href>`, elements with `onclick` containing `location.href`, attributes like `data-href`, `data-url`, router-like elements.
     - SPA hinting: detect `history.pushState` usage via DOM attributes and inline handlers.
   - Avoid **language-switch loops** (DE/EN/FR/IT path segments or `?lang=`) - canonicalize to first encountered language variant.
   - Score links by **menu keywords** (DE/EN/FR/IT) and restrict BFS (Breadth First Search).

2. **Menu detection & parsing (rules)**  
   - **Format detection**:  
     - `*.pdf` or `content-type: application/pdf` → `pdf`/`viewer` (if embedded).  
     - Embedded `<object|iframe type="application/pdf">` → `viewer`.  
     - Image-only hints → `image`.  
     - Otherwise → `integrated` (HTML).
   - **PDF text**: extract *first page only* via **PyMuPDF**. If no text → `pdf_image_unscannable`.  
   - **Language**: `langdetect` on text if > 50 chars.  
   - **Menu type**: keyword match (from `menutypes.json`), fallback to `"oct_menu"` when unclear.  
   - Compute a **confidence score** from (keyword score, format clarity, text length).

3. **Agentic fallback (LangChain + local OSS 20B)**  
   - Triggered if:
     - No menus found, or
     - All candidates have **low confidence** (below threshold), or
     - Conflicting signals (e.g., “Drinks” vs “Wine” classification).
   - **Prompted reasoning** over:
     - Page title & extracted text snippets (truncated),
     - Top N internal links with anchor/context,
     - Allowed **menu types** and **format** definitions,
     - Target languages (DE/EN/FR/IT/ZH),
     - Output schema (strict JSON).
   - Agent returns **ranked candidates** with predicted type/format/language.  
   - Crawler fetches those candidates and re-runs light parsing to confirm.

4. **Output** (single JSON file):
   - Per restaurant: name, url, `cookie_banner_accept`, `status`, `warnings`, array of `menus` (link, type, format, language[], pdf_button_text?, confidence).

---

## 4. Inputs

- `restaurants.json` (name → URL map).  
- `menutypes.json` (code → label).  
- `menuformat.json` (`pdf`, `viewer`, `integrated`).  
- `.env` with LLM params:
  - `OPENAI_API_BASE=http://localhost:1234/v1`
  - `OPENAI_MODEL=gpt-oss-20b`
  - `OPENAI_API_KEY=sk-noauth` (placeholder for LM Studio)

---

## 5. Non-Functional Requirements

- **Runtime**: 10–20 sites in < 10 minutes sequentially (no hard guarantee).  
- **Resource**: Single machine, Dockerized.  
- **Stability**: Skip gracefully on errors; always write a result entry with `status`.  
- **Reproducibility**: pinned `requirements.txt`, `Dockerfile`, `playwright install`.

---

## 6. Constraints & Assumptions

- Swiss-German context → multilingual sites common (DE/EN/FR/IT/ZH).  
- Depth limited to **2**; do not recurse further.  
- No OCR for images in this prototype.  
- Respect robots.txt *lightly* (log, but don’t block; interview scope).

---

## 7. Risks

- SPA-only navigation and router-driven links may hide URLs without clicks.  
- Language switch loops can still slip through (mitigated via canonicalization).  
- OSS 20B model may produce non-strict JSON → add parsing guardrails.  
- PDF viewers can obfuscate direct `.pdf` links.

---

## 8. Success Criteria

- For **2–3 example restaurants**, produce **valid JSON** with at least one correct menu (type, format, language) and cookie accept label when present.  
- Agentic fallback demonstrably improves results on a failing site (e.g., suggests correct menu link).

---

## 9. Future Work

- Image/PDF OCR (PaddleOCR/Cloud OCR) for image-only menus.  
- LangGraph agent with real tool-calling for controlled browsing.  
- Scheduling (Airflow/n8n) and review UI for low-confidence cases.  
- URL de-duplication across multi-language variants with site map crawling.

