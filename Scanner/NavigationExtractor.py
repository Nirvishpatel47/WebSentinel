#!/usr/bin/env python3
from playwright.async_api import Page, Locator
from typing import List

class NavigationExtractor:
    async def locate_interactive_nodes(self, page: Page) -> List[Locator]:
        """Finds dropdown selectors, buttons, and accessibility menus."""
        try:
            return await page.locator("button, [role='button'], [aria-expanded], [aria-haspopup], [aria-controls]").all()
        except:
            return []

    async def extract_element_signature(self, element: Locator) -> str:
        try:
            return await element.evaluate("""
                el => JSON.stringify({
                    tag: el.tagName, id: el.id, name: el.getAttribute('name'),
                    text: el.innerText?.trim().slice(0, 30)
                })
            """)
        except:
            return ""