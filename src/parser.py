from typing import List, Optional, Set, Dict, Tuple
from .models import LinkInfo, MenuItem
import re
import os
from .models import CrawlTask, LinkInfo, PageRecord
from bs4 import BeautifulSoup
import fitz
import requests
import io
from langdetect import detect as lang_detect
from .utils import guess_languages_from_text
from playwright.sync_api import Page
from .agent import MenuClassifier

class PageParserBase:
    """
    Base class for page parsers. Page parsers are used to parse the page, discover the menu items.

    """
    def __init__(self, page: Page, parent_link: CrawlTask, menutypes: Dict[str, str]):
        self.page = page
        self.parent_link = parent_link
        self.menutypes = menutypes

    def parse(self) -> Optional[MenuItem]:
        raise NotImplementedError("Subclasses must implement this method")

class PageParserFactory:
    def __init__(self, menutypes: Dict[str, str]):
        self.menutypes = menutypes

    def _is_special_accomodation_site(self, url: str) -> bool:
        return url.endswith("//gamper-restaurant.ch/")

    def get_parser(self, page: Page, parent_link: CrawlTask) -> PageParserBase:
        # check condition for the "special accomodation" sites, init the custom parser
        if self._is_special_accomodation_site(parent_link.url):
            return CustomPageParser(page, parent_link, self.menutypes)

        # checking if the link is a pdf (oversimplified)       
        if parent_link.url.endswith(".pdf"):
            return PDFPageParser(page, parent_link, self.menutypes)
        
        # naive image check
        if any(parent_link.url.endswith(ext) for ext in [".png",".jpg",".jpeg",".webp"]):
            return ImagePageParser(page, parent_link, self.menutypes)

        return WebPageParser(page, parent_link, self.menutypes)
    
class CustomPageParser(PageParserBase):
    """
    This parser is used for the "special accomodation" sites.
    """

    def parse(self) -> Optional[MenuItem]:
        # Gamper_Restaurant is a piece of art web site, and even 
        # full blown AI model failed to find the menu. We run the custom parser here
        # which already knows the menu.
        # if this is http://gamper-restaurant.ch/ restaturant page, then 
        # we return the predefined menu, and stop parsing.
        # otherwise, we return None.

        if self.parent_link.url.endswith("//gamper-restaurant.ch/"):
            return MenuItem(
                link="https://gamper-restaurant.ch/wermuteria", 
                type_code="oct_menu",
                type_label=self.menutypes.get("oct_menu", "Menu"),
                format="image",
                languages=["de"], 
                button_text="",
                confidence=0.9,  # yeah, I checked by myself last time, but who knows...
            )
        return None
    
class WebPageParser(PageParserBase):    
    def _safe_get_text_from_html(self, html: str, max_chars: int = 3500) -> str:
        soup = BeautifulSoup(html or "", "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        if max_chars and len(text) > max_chars:
            return text[:max_chars]
        return text

    def parse(self) -> Optional[MenuItem]:
        # the page was already loaded in the crawler
        # Feed the text to the classifier
        #   yes: return the menu item
        #   no: return None
        html = self.page.content()
        text = self._safe_get_text_from_html(html)
        # Create a temporary MenuClassifier instance using the centralized menutypes
        menu_item = MenuClassifier(self.menutypes).classify(
            site_name="Restaurant",  # We don't have site name in CrawlTask
            site_url=self.parent_link.url,
            page_url=self.parent_link.url,
            page_text=text,
            page_title=self.page.title(),
            menutypes=self.menutypes,
        )

        return menu_item

class PDFPageParser(PageParserBase):
    def _extract_pdf_first_page_text(self, pdf_url: str, timeout: int = 10, max_bytes: int = None) -> Tuple[str, Optional[str]]:
        """
        Download up to max_bytes (default from config) and extract text from first page.
        Returns tuple of (text, content_disposition) on success, ("", None) on failure.
        """
        max_bytes = max_bytes or int(os.getenv("MAX_PDF_BYTES", 1_000_000))
        try:
            print(f"DEBUG: Downloading PDF (max {max_bytes} bytes)...")
            r = requests.get(pdf_url, stream=True, timeout=timeout)
            r.raise_for_status()
            
            # Capture Content-Disposition header
            content_disposition = r.headers.get('Content-Disposition')
            if content_disposition:
                print(f"DEBUG: Content-Disposition header: {content_disposition}")
            
            content = io.BytesIO()
            read = 0
            for chunk in r.iter_content(16_384):
                if not chunk:
                    break
                content.write(chunk)
                read += len(chunk)
                if read >= max_bytes:
                    break
            content.seek(0)
            pdf_bytes = content.read()
            print(f"DEBUG: Downloaded {read} bytes, PDF bytes length: {len(pdf_bytes)}")
            print(f"DEBUG: First 100 bytes: {pdf_bytes[:100]}")
            
            # Try opening with fitz
            try:
                with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                    print(f"DEBUG: PDF opened successfully, page count: {doc.page_count}")
                    print(f"DEBUG: PDF metadata: {doc.metadata}")
                    if doc.page_count == 0:
                        print("DEBUG: PDF has 0 pages, trying alternative approach...")
                        # Try to get any text from the document
                        try:
                            # Sometimes PDFs have text but 0 pages reported
                            full_text = ""
                            for page_num in range(max(1, doc.page_count)):
                                try:
                                    page_text = doc.load_page(page_num).get_text("text")
                                    if page_text:
                                        full_text += page_text + "\n"
                                        print(f"DEBUG: Found text on page {page_num}: {len(page_text)} chars")
                                except Exception as e:
                                    print(f"DEBUG: Error loading page {page_num}: {e}")
                            if full_text.strip():
                                print(f"DEBUG: Alternative method found {len(full_text)} characters")
                                return full_text[:3500], content_disposition  # Apply our 3.5K limit
                        except Exception as e:
                            print(f"DEBUG: Alternative method failed: {e}")
                        return "", content_disposition
                    else:
                        print("DEBUG: Extracting text from first page...")
                        txt = doc.load_page(0).get_text("text") or ""
                        print(f"DEBUG: Extracted {len(txt)} characters of text")
                        
                        # small safety cap
                        max_chars = int(os.getenv("MAX_PDF_TEXT_CHARS", 3500))
                        if len(txt) > max_chars:
                            print(f"DEBUG: Truncating text from {len(txt)} to {max_chars} characters")
                            txt = txt[:max_chars]

                        print(f"****** Extracted PDF text from {pdf_url}:")
                        print("-" * 50)
                        print(txt)
                        print("-" * 50)
                        print(f"++++++++++++")
                    
                        return txt, content_disposition
            except Exception as e:
                print(f"DEBUG: Error opening PDF with fitz: {e}")
                return "", content_disposition
        except Exception as e:
            print(f"Error: Failed to extract text from PDF: {pdf_url}")
            print(f"Error details: {type(e).__name__}: {str(e)}")
            return "", None
        
    def detect_languages(self, text: str) -> list[str]:
        if not text or len(text) < 50:
            return guess_languages_from_text(text)
        langs = []
        try:
            lang = lang_detect(text)
            langs.append(lang[:2])
        except Exception:
            pass
        # heuristic enrich
        langs = list(dict.fromkeys(langs + guess_languages_from_text(text)))
        return langs or ["unknown"]

    def parse(self) -> Optional[MenuItem]:
        # Load beginning of the PDF
        text, content_disposition = self._extract_pdf_first_page_text(self.parent_link.url)
        languages = self.detect_languages(text)

        # Get page title safely - for PDFs, the page might not be navigated to the URL
        try:
            page_title = self.page.title()
        except Exception:
            page_title = "PDF Document"
            
        menu_item = MenuClassifier(self.menutypes).classify(
            site_name="Restaurant",  # We don't have site name in CrawlTask
            site_url=self.parent_link.url,
            page_url=self.parent_link.url,
            page_text=text,
            page_title=page_title,
            menutypes=self.menutypes,
            content_disposition=content_disposition,
        )

        # If MenuClassifier fails (e.g., LLM not available), create a basic menu item for PDFs
        if menu_item is None and text and len(text) > 100:
            menu_item = MenuItem(
                link=self.parent_link.url,
                type_code="oct_menu",
                type_label=self.menutypes.get("oct_menu", "Menu"),
                format="pdf",
                languages=languages,
                confidence=0.8,  # High confidence for PDFs since they're likely menus
                notes=f"PDF document with {len(text)} characters of text",
                content_disposition=content_disposition
            )

        return menu_item
    
class ImagePageParser(PageParserBase):
    def parse(self) -> Optional[MenuItem]:
        raise NotImplementedError("Ax example of a bespoke parser; not implemented")