#!/usr/bin/env python3
import logging
from urllib.parse import urlparse, urljoin, urldefrag, parse_qsl, urlencode
from playwright.async_api import Page
from typing import Dict, Set

logger = logging.getLogger(__name__)

class LinkExtractor:
    def __init__(self, base_url: str, allow_subdomains: bool = True):
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc.lower()
        self.allow_subdomains = allow_subdomains
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
        except Exception as e:
            logger.error(f"Failed to canonicalize URL {url}: {e}")
            return url

    def is_internal(self, url: str) -> bool:
        if url.startswith(("/", "#")): 
            return True
        try:
            link_domain = urlparse(url).netloc.lower()
            if self.allow_subdomains:
                return link_domain == self.base_domain or link_domain.endswith("." + self.base_domain)
            return link_domain == self.base_domain
        except Exception:
            return False

    async def extract(self, page: Page, current_url: str) -> Dict[str, Set[str]]:
        """Parses internal vs external link boundaries, including page canonical status."""
        # Step 1: Extract links along with metadata like rel attributes
        raw_elements = await page.evaluate("""() => {
            const links = [...document.querySelectorAll('a[href]')].map(a => ({
                href: a.getAttribute('href'),
                rel: a.getAttribute('rel') || ''
            }));
            const canonicalTag = document.querySelector('link[rel="canonical"]');
            const canonical = canonicalTag ? canonicalTag.getAttribute('href') : null;
            return { links, canonical };
        }""")
        
        internal = set()
        external = set()
        nofollow = set()

        if raw_elements["canonical"]:
            page_canonical = self.canonicalize(urljoin(current_url, raw_elements["canonical"]))

        for element in raw_elements["links"]:
            href = element["href"]
            rel = element["rel"].lower()

            if not href or any(href.lower().startswith(s) for s in self.skip_schemes):
                continue
                
            resolved = urljoin(current_url, href)
            canonical_url = self.canonicalize(resolved)

            if "nofollow" in rel:
                nofollow.add(canonical_url)

            if self.is_internal(canonical_url):
                internal.add(canonical_url)
            else:
                external.add(canonical_url)

        return {
            "page_canonical": page_canonical,
            "internal": internal, 
            "external": external,
            "nofollow": nofollow
        }
    
if __name__ == "__main__":
    import asyncio

    from playwright.async_api import async_playwright, Page
    TARGET_URL = "https://spreadme.institute/"
    
    async def main():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            print(f"Navigating browser to: {TARGET_URL}...")
            try:
                await page.goto(TARGET_URL, wait_until="domcontentloaded")
                
                extractor = LinkExtractor(base_url=TARGET_URL)
                
                results = await extractor.extract(page, current_url=TARGET_URL)
                
                print("\n--- EXTRACTION RESULTS ---")
                print(f"Canonical: {results['page_canonical']}")
                print(f"Internal links found: {results['internal']}")
                print(f"External links found: {results['external']}")
                print(f"Nofollow links flagged: {results['nofollow']}")
                
            except Exception as error:
                print(f"Execution failed! Ensure your local port 5501 server is running: {error}")
            finally:
                await browser.close()

    asyncio.run(main())