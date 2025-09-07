from __future__ import annotations
import re, urllib.parse
from typing import Iterable, Set, TypeVar, Callable, Any

LANG_SEGMENTS = re.compile(r"/(de|en|fr|it)(/|$)", re.IGNORECASE)
LANG_QUERY = re.compile(r"[?&](lang|language)=(de|en|fr|it)\b", re.IGNORECASE)

def normalize_url(base: str, url: str) -> str:
    return urllib.parse.urljoin(base, url)

def same_domain(root: str, url: str) -> bool:
    r = urllib.parse.urlparse(root)
    u = urllib.parse.urlparse(url)
    
    # Handle exact domain match
    if (u.netloc or r.netloc) == r.netloc:
        return True
    
    # Handle subdomain matches (e.g., media.chez-smith.ch should match chez-smith.ch)
    root_domain = r.netloc
    url_domain = u.netloc or r.netloc
    
    # Check if url_domain is a subdomain of root_domain
    if url_domain.endswith('.' + root_domain):
        return True
    
    return False

def canonicalize_language(url: str) -> str:
    """Normalize language-specific paths/queries to avoid DE<->EN loops."""
    parsed = urllib.parse.urlparse(url)
    path = LANG_SEGMENTS.sub("/", parsed.path)
    q = LANG_QUERY.sub("", parsed.query)
    rebuilt = parsed._replace(path=path, query=q)
    # drop trailing slashes duplicates
    final = urllib.parse.urlunparse(rebuilt)
    if final.endswith("//"):
        final = final[:-1]
    return final


def de_duplicate(seq: Iterable[str]) -> list[str]:
    seen: Set[str] = set()
    out = []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

T = TypeVar('T')

def deduplicate_by_key(items: Iterable[T], key_func: Callable[[T], Any]) -> list[T]:
    """
    Deduplicate items by a key function, keeping the first occurrence of each key.
    
    Args:
        items: Iterable of items to deduplicate
        key_func: Function that extracts the key from each item
        
    Returns:
        List of deduplicated items
    """
    seen = {}
    for item in items:
        key = key_func(item)
        if key not in seen:
            seen[key] = item
    return list(seen.values())

def guess_languages_from_text(s: str) -> list[str]:
    """Very light heuristic fallback (before langdetect)."""
    s_low = s.lower()
    langs = []
    if any(w in s_low for w in ["und", "speisekarte", "getränke", "wein", "mittagessen"]): langs.append("de")
    if any(w in s_low for w in ["and", "menu", "wine"]): langs.append("en")
    if any(w in s_low for w in ["et", "carte", "vin", "desserts"]): langs.append("fr")
    if any(w in s_low for w in ["e", "vino", "carta"]): langs.append("it")
    return de_duplicate(langs)[:3]
