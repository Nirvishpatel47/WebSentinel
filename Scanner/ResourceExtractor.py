#!/usr/bin/env python3
from urllib.parse import urljoin
from playwright.async_api import Page
from typing import Dict, List, Set

class ResourceExtractor:
    async def extract_dom_resources(self, page: Page) -> Dict[str, List[str]]:
        return await page.evaluate("""
        () => {
            const getAttr = (sel, attr) => [...document.querySelectorAll(sel)].map(e => e.getAttribute(attr)).filter(Boolean);
            return {
                images: [...getAttr('img[src]', 'src'), ...getAttr('img[data-src]', 'data-src'), ...getAttr('img[data-lazy-src]', 'data-lazy-src')],
                scripts: getAttr('script[src]', 'src'),
                styles: getAttr('link[rel="stylesheet"]', 'href'),
                videos: [...getAttr('video[src]', 'src'), ...getAttr('video source[src]', 'src')],
                audios: [...getAttr('audio[src]', 'src'), ...getAttr('audio source[src]', 'src')],
                iframes: getAttr('iframe[src]', 'src'),
                posters: getAttr('video[poster]', 'poster'),
                pictures: getAttr('picture source[srcset]', 'srcset')
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