#!/usr/bin/env python3
import json
import logging
from playwright.async_api import Page, Locator
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class NavigationExtractor:
    async def locate_interactive_nodes(self, page: Page) -> List[Locator]:
        """Finds dropdown selectors, buttons, accessibility menus, and common interactive mock tags."""
        try:
            selector = (
                "button, [role='button'], [aria-expanded], [aria-haspopup], [aria-controls], "
                "nav div, nav li, .menu-item, .btn"
            )
            return await page.locator(selector).all()
        except Exception as e:
            logger.error(f"Failed to query interactive elements on page: {e}")
            return []

    async def extract_element_signature(self, element: Locator) -> Optional[str]:
        """Extracts stable structural identity markers to safely finger-print the element."""
        try:
            raw_json = await element.evaluate("""
                el => {
                    return JSON.stringify({
                        tag: el.tagName ? el.tagName.toLowerCase() : '',
                        id: el.id || '',
                        name: el.getAttribute('name') || '',
                        role: el.getAttribute('role') || '',
                        class: el.className && typeof el.className === 'string' ? el.className.trim() : '',
                        text: el.innerText ? el.innerText.trim().replace(/\\s+/g, ' ').slice(0, 50) : '',
                        placeholder: el.getAttribute('placeholder') || ''
                    });
                }
            """)
            return raw_json
        except Exception as e:
            logger.debug(f"Element detached or mutated before signature collection completed: {e}")
            return None

if __name__ == "__main__":
    import asyncio
    import json
    from playwright.async_api import async_playwright

    async def test_navigation_pipeline():
        TARGET_URL = "http://127.0.0.1:5501/TESTING/Website-5/contact.html"
        extractor = NavigationExtractor()

        async with async_playwright() as p:
            print("Initializing headless browser engine...")
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            print(f"Navigating to target environment: {TARGET_URL}")
            await page.goto(TARGET_URL, wait_until="domcontentloaded")
            
            # 1. Discover all matching components
            nodes = await extractor.locate_interactive_nodes(page)
            print(f"Extraction Step Complete: Found {len(nodes)} interactable layout elements.")
            
            # 2. Compile fingerprints to ensure unique structural representation
            print("\n=== SYSTEM SIGNATURE FINGERPRINTS (FIRST 10) ===")
            valid_signatures_count = 0
            
            for node in nodes:
                signature_str = await extractor.extract_element_signature(node)
                if not signature_str:
                    continue
                    
                valid_signatures_count += 1
                if valid_signatures_count <= 10:
                    # Deserialize to display formatted object layouts
                    parsed_data = json.loads(signature_str)
                    print(f"Element #{valid_signatures_count}:")
                    print(f"  Tag:        <{parsed_data['tag']}>")
                    print(f"  ID/Name:    ID: '{parsed_data['id']}' | Name: '{parsed_data['name']}'")
                    print(f"  Classes:    [{parsed_data['class']}]")
                    print(f"  Text Content: '{parsed_data['text']}'")
                    print("-" * 50)
                    
            print(f"Validation complete. Successfully fingerprinted {valid_signatures_count} elements.")
            await browser.close()

    if __name__ == "__main__":
        asyncio.run(test_navigation_pipeline())