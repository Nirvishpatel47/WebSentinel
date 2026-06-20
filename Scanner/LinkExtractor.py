#!/usr/bin/env python3
from urllib.parse import urlparse, urljoin, urldefrag, parse_qsl, urlencode
from playwright.async_api import Page
from typing import Dict, Set

class LinkExtractor:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc.lower()
        self.strip_params = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "fbclid", "gclid"}
        self.skip_schemes = {"blob", "data", "javascript", "mailto", "tel", "sms", "whatsapp"}

    def canonicalize(self, url: str) -> str:
        try:
            defragged, _ = urldefrag(url.strip())
            parsed = urlparse(defragged)
            queries = parse_qsl(parsed.query)
            clean_queries = [(k, v) for k, v in queries if k.lower() not in self.strip_params]
            new_query = urlencode(sorted(clean_queries))
            return parsed._replace(query=new_query).geturl()
        except:
            return url

    def is_internal(self, url: str) -> bool:
        if url.startswith(("/", "#")): return True
        try:
            return urlparse(url).netloc.lower() == self.base_domain
        except:
            return False

    async def extract(self, page: Page, current_url: str) -> Dict[str, Set[str]]:
        """Parses internal vs external link boundaries."""
        raw_hrefs = await page.evaluate("() => [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href'))")
        internal = set()
        external = set()

        for href in raw_hrefs:
            if not href or any(href.lower().startswith(s) for s in self.skip_schemes):
                continue
            resolved = urljoin(current_url, href)
            canonical = self.canonicalize(resolved)

            if self.is_internal(canonical):
                internal.add(canonical)
            else:
                external.add(canonical)

        return {"internal": internal, "external": external}