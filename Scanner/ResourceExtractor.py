#!/usr/bin/env python3
from urllib.parse import urljoin
from playwright.async_api import Page
from typing import Dict, List, Set

class ResourceExtractor:
    async def extract_dom_resources(self, page: Page) -> Dict[str, List[str]]:
        return await page.evaluate("""
        () => {
            const getAttr = (sel, attr) => [...document.querySelectorAll(sel)].map(e => e.getAttribute(attr)).filter(Boolean);
            
            // Helper to pull URLs out of responsive srcset text strings
            const parseSrcset = (sel) => [...document.querySelectorAll(sel)]
                .map(e => e.getAttribute('srcset'))
                .filter(Boolean)
                .flatMap(srcset => srcset.split(',').map(s => s.trim().split(' ')[0]));

            return {
                images: [
                    ...getAttr('img[src]', 'src'), 
                    ...getAttr('img[data-src]', 'data-src'), 
                    ...getAttr('img[data-lazy-src]', 'data-lazy-src'),
                    ...getAttr('img[data-original]', 'data-original'),
                    ...parseSrcset('img[srcset]'),
                    ...parseSrcset('picture source[srcset]')
                ],
                scripts: getAttr('script[src]', 'src'),
                styles: getAttr('link[rel="stylesheet"]', 'href'),
                videos: [...getAttr('video[src]', 'src'), ...getAttr('video source[src]', 'src')],
                audios: [...getAttr('audio[src]', 'src'), ...getAttr('audio source[src]', 'src')],
                iframes: getAttr('iframe[src]', 'src'),
                posters: getAttr('video[poster]', 'poster'),
                embeds: [...getAttr('object[data]', 'data'), ...getAttr('embed src', 'src')]
            };
        }
        """)

    def map_to_global(self, current_url: str, raw_resources: Dict[str, List[str]], network_urls: Set[str], global_map: Dict[str, Dict], linker):
        """Merges extracted asset nodes into a global mapping space."""
        for category, items in raw_resources.items():
            for raw in items:
                if any(raw.lower().startswith(s) for s in linker.skip_schemes): continue
                abs_url = urljoin(current_url, raw)
                canonical = linker.canonicalize(abs_url)
                if canonical not in global_map:
                    global_map[canonical] = {"found_on": current_url, "resource_type": category}

        for net_url in network_urls:
            canonical_net = linker.canonicalize(net_url)
            if canonical_net not in global_map:
                global_map[canonical_net] = {"found_on": current_url, "resource_type": "network"}

if __name__ == "__main__":
    import asyncio
    from urllib.parse import urlparse, urldefrag, parse_qsl
    from playwright.async_api import async_playwright

    class MockLinker:
        def __init__(self):
            self.skip_schemes = {"mailto", "tel", "javascript", "data", "sms"}
        def canonicalize(self, url: str) -> str:
            try:
                defragged, _ = urldefrag(url.strip())
                parsed = urlparse(defragged)
                return parsed.geturl()
            except:
                return url
            
    async def test_resource_extractor():
        TARGET_URL = "http://127.0.0.1:5501/TESTING/Website-5/about.html"
        
        global_map = {}
        linker = MockLinker()
        extractor = ResourceExtractor()

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            captured_network: Set[str] = set()
            page.on("request", lambda request: captured_network.add(request.url))
            
            print(f"Navigating headless browser to: {TARGET_URL}")
            await page.goto(TARGET_URL, wait_until="domcontentloaded")
            
            raw_resources = await extractor.extract_dom_resources(page)
            
            extractor.map_to_global(
                current_url=TARGET_URL,
                raw_resources=raw_resources,
                network_urls=captured_network,
                global_map=global_map,
                linker=linker
            )
            
            print("\n=== EXTRACTED DOM RESOURCES RAW COUNTS ===")
            for category, items in raw_resources.items():
                print(f"- {category.capitalize()}: {len(items)} items found")

            print("\n=== SAMPLE ENTRIES MAPPED TO GLOBAL SPACE (FIRST 15) ===")
            for index, (url, metadata) in enumerate(global_map.items()):
                if index >= 15:
                    break
                print(f"[{metadata['resource_type'].upper()}] -> {url}")
                
            await browser.close()
    asyncio.run(test_resource_extractor())