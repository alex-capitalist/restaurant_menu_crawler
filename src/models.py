from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional

class MenuItem(BaseModel):
    link: str
    type_code: str
    type_label: str
    format: str
    languages: List[str] = Field(default_factory=list)
    button_text: Optional[str] = None
    confidence: float = 0.0
    notes: Optional[str] = None
    content_disposition: Optional[str] = None

class RestaurantResult(BaseModel):
    name: str
    url: str
    cookie_banner_accept: Optional[str] = None
    status: str = "ok"
    warnings: List[str] = Field(default_factory=list)
    menus: List[MenuItem] = Field(default_factory=list)

class CrawlTask(BaseModel):
    """Represents a URL to be crawled with its navigation context."""
    url: str
    depth: int
    call_stack: List[str] = Field(default_factory=list)
    
    def __str__(self) -> str:
        return f"CrawlTask(url={self.url}, depth={self.depth}, stack_len={len(self.call_stack)})"

class LinkInfo(BaseModel):
    """Represents a link found on a page with its text."""
    url: str
    text: str = ""
    
    def __str__(self) -> str:
        return f"LinkInfo(url={self.url}, text='{self.text[:30]}...')"

class PageRecord(BaseModel):
    """Represents the data collected from a crawled page."""
    url: str
    title: str = ""
    html: str = ""
    text: str = ""
    links: List[LinkInfo] = Field(default_factory=list)
    pdf_embeds: List[str] = Field(default_factory=list)
    has_menu_pdfs: bool = False
    call_stack: List[str] = Field(default_factory=list)
    error: Optional[str] = None
    
    def __str__(self) -> str:
        return f"PageRecord(url={self.url}, links={len(self.links)}, pdfs={len(self.pdf_embeds)})"