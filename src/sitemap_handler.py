from __future__ import annotations
from typing import Dict, List, Tuple, Optional
from playwright.sync_api import sync_playwright, Page
from bs4 import BeautifulSoup
import re, time, urllib.parse
from .utils import normalize_url, same_domain, canonicalize_language
# Removed non-existent classifier import
from .models import CrawlTask, LinkInfo, PageRecord

class SitemapHandler:
    def parse_sitemap_xml(self, content: str, base_url: str) -> List[Tuple[str, str]]:
        """Parse XML sitemap content and extract URLs with optional text."""
        urls = []
        try:
            # Try lxml first, fallback to html.parser if not available
            try:
                soup = BeautifulSoup(content, "xml")
            except Exception:
                # Fallback to html.parser if lxml is not available
                soup = BeautifulSoup(content, "html.parser")
            
            # Handle sitemap index files (contain references to other sitemaps)
            sitemap_refs = soup.find_all("sitemap")
            for ref in sitemap_refs:
                loc = ref.find("loc")
                if loc and loc.text:
                    urls.append((loc.text.strip(), "sitemap"))
            
            # Handle regular sitemap entries
            url_entries = soup.find_all("url")
            for entry in url_entries:
                loc = entry.find("loc")
                if loc and loc.text:
                    url = loc.text.strip()
                    # Try to extract meaningful text from lastmod, changefreq, or priority
                    text_parts = []
                    lastmod = entry.find("lastmod")
                    if lastmod and lastmod.text:
                        text_parts.append(f"lastmod: {lastmod.text.strip()}")
                    changefreq = entry.find("changefreq")
                    if changefreq and changefreq.text:
                        text_parts.append(f"freq: {changefreq.text.strip()}")
                    priority = entry.find("priority")
                    if priority and priority.text:
                        text_parts.append(f"priority: {priority.text.strip()}")
                    
                    text = " | ".join(text_parts) if text_parts else ""
                    urls.append((url, text))
            
            # If no URLs found with BeautifulSoup, try regex fallback for malformed XML
            if not urls:
                import re
                # Look for URLs in the content using regex
                url_pattern = r'https?://[^\s<>"\']+'
                found_urls = re.findall(url_pattern, content)
                for url in found_urls:
                    if same_domain(base_url, url):
                        urls.append((url, "regex_fallback"))
                    
        except Exception as e:
            print(f"Error parsing sitemap XML: {e}")
            # Last resort: try to extract URLs using regex
            try:
                import re
                url_pattern = r'https?://[^\s<>"\']+'
                found_urls = re.findall(url_pattern, content)
                for url in found_urls:
                    if same_domain(base_url, url):
                        urls.append((url, "regex_fallback"))
            except Exception:
                pass
        
        return urls

    def parse_robots_txt(self, content: str, base_url: str) -> List[str]:
        """Parse robots.txt content to find sitemap references."""
        sitemaps = []
        try:
            for line in content.split('\n'):
                line = line.strip()
                if line.lower().startswith('sitemap:'):
                    sitemap_url = line[8:].strip()
                    if sitemap_url:
                        sitemaps.append(sitemap_url)
        except Exception as e:
            print(f"Error parsing robots.txt: {e}")
        
        return sitemaps
    
    def get_sitemap_candidates(self, base_url: str) -> List[str]:
        """Generate common sitemap URL candidates for a given base URL."""
        parsed = urllib.parse.urlparse(base_url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        
        candidates = [
            f"{base}/sitemap.xml",
            f"{base}/sitemap_index.xml", 
            f"{base}/sitemap-index.xml",
            f"{base}/sitemap/sitemap.xml",
            f"{base}/sitemaps/sitemap.xml",
            f"{base}/sitemap.txt",
            f"{base}/sitemap/sitemap.txt",
            f"{base}/robots.txt"  # robots.txt often contains sitemap references
        ]
        
        # Add language-specific variants if URL has language segments
        if re.search(r"/(de|en|fr|it)(/|$)", base_url, re.IGNORECASE):
            for lang in ["de", "en", "fr", "it"]:
                candidates.extend([
                    f"{base}/{lang}/sitemap.xml",
                    f"{base}/sitemap_{lang}.xml"
                ])
        
        return candidates

    def discover_sitemap_urls(self, page: Page, base_url: str) -> List[Tuple[str, str]]:
        """Attempt to discover and load sitemap URLs from common locations."""
        discovered_urls = []
        processed_sitemaps = set()  # Avoid processing the same sitemap multiple times
        
        # Get sitemap candidates
        candidates = self.get_sitemap_candidates(base_url)
        
        for candidate_url in candidates:
            if candidate_url in processed_sitemaps:
                continue
            processed_sitemaps.add(candidate_url)
            
            try:
                # Try to load the candidate URL
                response = page.goto(candidate_url, wait_until="networkidle", timeout=10000)
                
                if response and response.status == 200:
                    content = page.content()
                    content_type = response.headers.get('content-type', '').lower()
                    
                    if 'xml' in content_type or candidate_url.endswith('.xml'):
                        # Parse as XML sitemap
                        urls = self.parse_sitemap_xml(content, base_url)
                        discovered_urls.extend(urls)
                        print(f"Found {len(urls)} URLs in sitemap: {candidate_url}")
                        
                    elif candidate_url.endswith('robots.txt'):
                        # Parse robots.txt for sitemap references
                        sitemap_refs = self.parse_robots_txt(content, base_url)
                        for ref in sitemap_refs:
                            if ref not in processed_sitemaps:
                                processed_sitemaps.add(ref)
                                try:
                                    # Try to load the referenced sitemap
                                    ref_response = page.goto(ref, wait_until="networkidle", timeout=10000)
                                    if ref_response and ref_response.status == 200:
                                        ref_content = page.content()
                                        ref_urls = self.parse_sitemap_xml(ref_content, base_url)
                                        discovered_urls.extend(ref_urls)
                                        print(f"Found {len(ref_urls)} URLs in referenced sitemap: {ref}")
                                except Exception as e:
                                    print(f"Failed to load referenced sitemap {ref}: {e}")
                                
                    elif candidate_url.endswith('.txt'):
                        # Parse as text sitemap (one URL per line)
                        text_urls = []
                        for line in content.split('\n'):
                            line = line.strip()
                            if line and not line.startswith('#'):
                                text_urls.append((line, "sitemap"))
                        discovered_urls.extend(text_urls)
                        print(f"Found {len(text_urls)} URLs in text sitemap: {candidate_url}")
                        
            except Exception as e:
                # Silently continue if sitemap doesn't exist or fails to load
                continue
        
        # Filter to same domain and canonicalize
        filtered_urls = []
        for url, text in discovered_urls:
            if same_domain(base_url, url):
                canonical_url = canonicalize_language(url)
                filtered_urls.append((canonical_url, text))
        
        return filtered_urls