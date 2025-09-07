from __future__ import annotations
from typing import Optional
from playwright.sync_api import Page

class CookieDetector:
    def __init__(self):
        self.COOKIE_BUTTON_PATTERNS = [
            "accept", "agree", "ok", "allow", "alle akzeptieren", "akzeptieren",
            "zustimmen", "accepter", "d'accord", "accetta", "consenti"
        ]

    def detect(self, page: Page) -> Optional[str]:
        # Try common selectors quickly
        # Look for any button inside containers mentioning cookies
        candidates = page.locator("text=/cookie/i").locator("xpath=..").locator("button, [role='button']")
        try:
            count = candidates.count()
        except Exception:
            count = 0
        if count:
            for i in range(min(count, 5)):
                txt = candidates.nth(i).inner_text(timeout=1000).strip()
                if any(pat in txt.lower() for pat in self.COOKIE_BUTTON_PATTERNS):
                    return txt

        # Fallback: search all buttons by text
        btns = page.locator("button, [role='button'], input[type='button'], input[type='submit']")
        try:
            n = btns.count()
        except Exception:
            n = 0
        for i in range(min(n, 20)):
            try:
                txt = btns.nth(i).inner_text(timeout=500).strip()
            except Exception:
                continue
            low = txt.lower()
            if "cookie" in low or any(p in low for p in self.COOKIE_BUTTON_PATTERNS):
                return txt
        return None