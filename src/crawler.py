from typing import List, Optional, Set, Dict, Tuple
from .models import LinkInfo, MenuItem
from .utils import normalize_url, same_domain, canonicalize_language, deduplicate_by_key
from playwright.sync_api import sync_playwright, Page
import re
import os
from .sitemap_handler import SitemapHandler
from .cookie_detector import CookieDetector
from .models import CrawlTask, LinkInfo, PageRecord
from bs4 import BeautifulSoup
import os

from .link_extractor import LinkExtractor, LinkNoiseFilter
from .parser import PageParserFactory

class SiteCrawler:
    def __init__(self, restaurant_name: str, restaurant_url: str, menutypes: Dict[str, str]):
        self.restaurant_name = restaurant_name
        self.restaurant_url = restaurant_url
        self.menutypes = menutypes
        
        # Load max_depth from environment variable
        self.max_depth = int(os.getenv("MAX_CRAWL_DEPTH", "3"))
        
        self._link_extractor = LinkExtractor(max_depth=self.max_depth)
        self._link_noise_filter = LinkNoiseFilter()
        self._page_parser_factory = PageParserFactory(menutypes)
        self._cookie_detector = CookieDetector()
        self._cookie_accept: Optional[str] = None
        self._queue: List[CrawlTask] = []
        self._visited_links: Set[str] = set()
        self._seen_links: Set[str] = set()
        self._menu_items: List[MenuItem] = []
        
        self._queue.append(CrawlTask(url=restaurant_url, depth=0, call_stack=[]))

    def _deduplicate_menu_items(self):
        self._menu_items = deduplicate_by_key(self._menu_items, lambda item: item.link)

    def _detect_cookie_accept_button(self, page: Page) -> Optional[str]:
        """
        Find pages with menus and mark their parents for exclusion
        """
        if self._cookie_accept is None:
            cookie_accept = self._cookie_detector.detect(page)
            # Optionally click it if visible
            if cookie_accept:
                try:
                    page.get_by_role("button", name=re.compile(cookie_accept, re.I)).first.click(timeout=1000)
                except Exception:
                    pass

    def _is_web_page_naive(self, url: str) -> bool:
        """
        Check if URL points to a web page that can be loaded with Playwright.
        Returns True for web pages, False for non-web files (PDFs, images, etc.)
        """
        # Common file extensions that shouldn't be loaded as web pages
        non_web_extensions = {
            '.pdf', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp',
            '.txt', '.csv', '.json', '.xml'
        }
        
        # Extract the path and query parameters
        url_lower = url.lower()
        
        # Check if URL ends with any of the non-web extensions
        for ext in non_web_extensions:
            if url_lower.endswith(ext):
                return False  # This is NOT a web page
                
        # Check for common patterns in the path
        non_web_patterns = [
            r'\.pdf(\?|$|#)',
            r'\.(png|jpg|jpeg|gif|bmp|svg|webp)(\?|$|#)',
        ]
        
        for pattern in non_web_patterns:
            if re.search(pattern, url_lower):
                return False  # This is NOT a web page
                
        return True  # This is a web page

    def _exclude_child_pages(self, menu_items: List[MenuItem], current_depth: int):
        """Exclude child pages only if we find specific menu types, not generic menus"""
        for item in menu_items:
            # Only exclude if this is a specific menu type (not generic "oct_menu")
            # Get all menu types except the generic "oct_menu"
            specific_menu_types = [code for code in self.menutypes.keys() if code != "oct_menu"]
            should_exclude = (
                current_depth > 1 and  # Don't exclude if we're on a landing page
                item.confidence >= 0.7 and  # Don't exclude if confidence is low
                item.type_code in specific_menu_types  # Only exclude specific menu types
            )
            
            if should_exclude:
                self._visited_links.add(canonicalize_language(item.link))

    def crawl_site(self):
        sitemap_handler = SitemapHandler()
        # We need to create a page first to call discover_sitemap_urls
        # For now, we'll skip sitemap discovery and just use the initial URL
        sitemap_urls = []

        # TODO: we seem not using sitemap URLs at all
        # Potentially too heavy operation, since the website could have a lot of sitemap URLs
        # we can limit the number of sitemap URLs to be crawled
        # or we can limit the nested level of the sitemap URLs
        for url, text in sitemap_urls:
            self._queue.append(CrawlTask(url=url, depth=1, call_stack=[]))

        with sync_playwright() as p:
            print(f"Launching browser....")


            browser = p.chromium.launch(headless=True)
            ctx = browser.new_context()
            page = ctx.new_page()
            pages: Dict[str, PageRecord] = {}

            while self._queue:
                task = self._queue.pop(0)
                if task.depth > self.max_depth:
                    continue

                norm_url = canonicalize_language(task.url)
                if norm_url in self._visited_links:
                    continue
                

                # Update call stack for this page
                current_call_stack = task.call_stack + [norm_url]

                # Skip non-web files (PDFs, images, etc.) that shouldn't be loaded with Playwright
                if self._is_web_page_naive(task.url):
                    # wait until the page is completely loaded
                    try:
                        # Try with domcontentloaded first (faster), then fallback to networkidle
                        try:
                            page.goto(task.url, wait_until="domcontentloaded", timeout=15000)
                        except Exception:
                            page.goto(task.url, wait_until="networkidle", timeout=60000)
                    except Exception as e:
                        pages[norm_url] = PageRecord(url=norm_url, error=f"nav_error: {e}")
                        continue

                    # Detect cookie banner accept button (once)
                    self._detect_cookie_accept_button(page)

                    extracted_links = self._link_extractor.extract_links(page, task)

                    print(f"****** Extracted links: {len(extracted_links)}")
                    print("***********")
                    
                    # Filter out already processed links (both queued and visited)
                    unvisited_links = []
                    for link in extracted_links:
                        norm_url = canonicalize_language(link.url)
                        if norm_url not in self._seen_links:
                            self._seen_links.add(norm_url)
                            unvisited_links.append(link)
                    extracted_links = unvisited_links

                    filtered_links = self._link_noise_filter.filter_links(extracted_links)
                    # crawl the unvisited links
                    for link in filtered_links:
                        candidate_task = CrawlTask(
                            url=link.url, 
                            depth=task.depth + 1, 
                            call_stack=current_call_stack
                        )
                        self._queue.append(candidate_task)
                        print(f"****** Queued link: {link.url}")

                print(f"~~~~~~~~ current queued links: {self._queue}")


                print(f"+++++ get parser link: {task.url}")
                candidate_page_parser = self._page_parser_factory.get_parser(page, task)
                menu_item = candidate_page_parser.parse()
                if menu_item:
                    self._menu_items.append(menu_item)
                    # print(f"+++++ menu item: {menu_item.link}")
                    # self._exclude_child_pages([menu_item], task.depth)

                self._deduplicate_menu_items()
            
                self._visited_links.add(norm_url)
