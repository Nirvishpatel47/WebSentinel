#!/usr/bin/env python3
from playwright.async_api import Page, Locator
from typing import Set

class InteractionEngine:
    def __init__(self, max_interactions_per_page: int = 20):
        self.max_interactions = max_interactions_per_page

    async def reveal_hidden_dom(self, page: Page, nodes: list, nav_extractor, callback_on_delta):
        """Fires hovers and click events systematically to uncover structural elements."""
        seen_signatures: Set[str] = set()
        executed_count = 0

        for node in nodes:
            if executed_count >= self.max_interactions:
                break
            try:
                if not await node.is_visible(): continue
                sig = await nav_extractor.extract_element_signature(node)
                if not sig or sig in seen_signatures: continue
                seen_signatures.add(sig)

                # Execute hover interaction
                try:
                    await node.hover(timeout=300)
                    await page.wait_for_timeout(150)
                except: pass

                # Execute explicit toggle clicks if signature tags match menus
                aria = await node.get_attribute("aria-expanded")
                role = await node.get_attribute("role") or ""
                cls = (await node.get_attribute("class") or "").lower()

                if aria is not None or "menu" in cls or "dropdown" in cls or "accordion" in cls or role == "button":
                    await node.click(timeout=400)
                    await page.wait_for_timeout(250)
                    executed_count += 1
                    
                    # Notify supervisor that DOM state changed
                    await callback_on_delta()

                try:
                    await page.keyboard.press("Escape")
                except: pass
            except:
                continue