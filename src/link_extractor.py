from typing import List, Optional, Set, Dict, Tuple
from .models import LinkInfo, MenuItem
from .agent import NoiseClassifier
from .utils import normalize_url, same_domain, canonicalize_language, deduplicate_by_key
from playwright.sync_api import sync_playwright, Page
import re
import os
from .sitemap_handler import SitemapHandler
from .cookie_detector import CookieDetector
from .models import CrawlTask, LinkInfo, PageRecord
from bs4 import BeautifulSoup
import fitz
import requests
import io

class LinkExtractor:
    """
    This class is used to extract the links from the page.
    """
    def __init__(self, max_depth: int = 3):
        self.max_depth = max_depth

    def _extract_links_from_dom(self, page: Page, base_url: str) -> List[LinkInfo]:
        """Return list of LinkInfo objects found in anchors and clickable elements."""
        links: List[LinkInfo] = []

        # <a href>
        anchors = page.eval_on_selector_all("a[href]", "els => els.map(e => ({href: e.getAttribute('href'), text: e.innerText}))")
        for a in anchors:
            href = a.get("href") or ""
            txt = (a.get("text") or "").strip()
            if href:
                links.append(LinkInfo(url=normalize_url(base_url, href), text=txt))

        # Elements with onclick containing window.location / location.href / open('...')
        onclicks = page.eval_on_selector_all("[onclick]", "els => els.map(e => e.getAttribute('onclick'))")
        for oc in onclicks:
            if not oc: continue
            # naive regex for URL-like strings in onclick
            m = re.findall(r"""['"](/[^'"]+|https?://[^'"]+)['"]""", oc)
            for cand in m:
                links.append(LinkInfo(url=normalize_url(base_url, cand), text=""))

        # data-href / data-url
        data_links = page.eval_on_selector_all("[data-href], [data-url]", "els => els.map(e => e.getAttribute('data-href') || e.getAttribute('data-url'))")
        for d in data_links:
            if d:
                links.append(LinkInfo(url=normalize_url(base_url, d), text=""))

        # role="link" with aria href in dataset (rare but seen)
        role_links = page.eval_on_selector_all('[role="link"]', "els => els.map(e => ({txt: e.innerText, href: e.getAttribute('href')}))")
        for rl in role_links:
            if rl.get("href"):
                links.append(LinkInfo(url=normalize_url(base_url, rl["href"]), text=(rl.get("txt") or "").strip()))

        # Clean dupes
        return deduplicate_by_key(links, lambda link: link.url)

    def _extract_pdf_links_from_page(self, soup: BeautifulSoup, url: str) -> List[LinkInfo]:
        # Extract embeds: pdf/object/iframe
        pdf_embeds = []
        for obj in soup.find_all(["embed","object","iframe"]):
            src = obj.get("src") or obj.get("data") or ""
            if "pdf" in (obj.get("type") or "").lower() or src.lower().endswith(".pdf") or "pdfjs" in src.lower() or "viewer" in src.lower():
                if src:
                    # Normalize the URL to make it absolute
                    normalized_src = normalize_url(url, src)
                    pdf_embeds.append(normalized_src)
        
        # Also extract PDF links from anchor tags
        for anchor in soup.find_all("a", href=True):
            href = anchor.get("href", "")
            if href.lower().endswith(".pdf"):
                # Normalize the URL to make it absolute
                normalized_href = normalize_url(url, href)
                pdf_embeds.append(normalized_href)

        # Clean dupes
        return deduplicate_by_key(
            [LinkInfo(url=url, text="") for url in pdf_embeds], 
            lambda link: link.url
        )

    def extract_links(self, page: Page, task: CrawlTask) -> List[LinkInfo]:
        # 1) Is the current nested level is the deepest level?
        #   yes: return empty list
        if task.depth > self.max_depth:
            return []

        # 2) Find all links on the page and return them.
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")
        links = self._extract_links_from_dom(page, task.url)
        pdf_links = self._extract_pdf_links_from_page(soup, task.url)

        # Filter links to same domain only
        all_links = links + pdf_links
        same_domain_links = []
        for link in all_links:
            if same_domain(task.url, link.url):
                same_domain_links.append(link)

        # deduplicate the links
        return deduplicate_by_key(same_domain_links, lambda link: link.url)

class LinkNoiseFilter:
    def __init__(self):
        self._noise_classifier = NoiseClassifier()

    def filter_links(self, links: List[LinkInfo]) -> List[LinkInfo]:
        # brute force heuristics to filter out sure non-menu links
        exclude_patterns = [
            "grundriss", "floor", "plan", "layout", "map", 
            "document", "doc", "manual", "handbook", "guide", "anleitung", "bedienungsanleitung",
            "contract", "agreement", "terms", "conditions", "privacy", "datenschutz",
            "invoice", "bill", "receipt", "quittung", "rechnung", "facture",
            "vitrine", "tapas", "events", "news", "gallery", "printers",
            "agb", "infos", "about", "contact", "faq", "help", "support", "kontakt", 
            "impressum", "reservation", "reservierung", "booking", "buchung", "reservieren",
            "tel.", "mailto:",
        ]

        filtered_links = []

        for link in links:
            if any(pattern in link.text for pattern in exclude_patterns):
                continue           
            if any(pattern in link.url for pattern in exclude_patterns):
                continue
            
            filtered_links.append(link)

        # filter out the image links, we don't support them in this version
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico'}
        filtered_links = [link for link in filtered_links if not any(link.url.lower().endswith(ext) for ext in image_extensions)]

        # feed the rest of the links to the noise classifier
        classified_links = self._noise_classifier.classify(filtered_links)

        # Return the filtered LinkInfo objects - the filtering is already done in the classifier
        return classified_links

