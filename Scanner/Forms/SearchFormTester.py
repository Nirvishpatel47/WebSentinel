#!/usr/bin/env python3
import time
from playwright.async_api import Page, Locator
from typing import List, Dict, Any

class SearchFormTester:
    """
    Responsibility: Dispatches lookup phrases and verifies search result output views.
    """
    async def test(self, page: Page, form_locator: Locator, fields: List[Dict[str, Any]]) -> Dict[str, Any]:
        start_time = time.time()
        messages = []
        errors = []
        success = False

        try:
            # 1. Populate the designated search query box
            search_input = None
            for field in fields:
                if field['type'] in ['text', 'search'] or any(kw in field['name'].lower() for kw in ['q', 'search', 'query']):
                    search_input = form_locator.locator(f"input[name='{field['name']}']").first if field['name'] else form_locator.locator("input").first
                    break

            if search_input and await search_input.is_visible():
                await search_input.fill("WebSentinel_Validation_Query")
                messages.append("Diagnostic test query string passed to search input node element.")
            else:
                errors.append("Could not map structural text input capture field container within search layout block.")

            # 2. Execute submission via enter key stroke to mimic natural search patterns
            if search_input:
                await search_input.press("Enter")
                await page.wait_for_timeout(1500)  # Higher interval allocation for lookup processing overhead
                messages.append("Search query string fired via keyboard execution context layer.")

                # 3. Structural validation verification check of resulting target state
                resulting_url = page.url.lower()
                resulting_html = (await page.content()).lower()
                
                if "query" in resulting_url or "search" in resulting_url or "websentinel" in resulting_html:
                    success = True
                    messages.append("Search functionality cleared: Layout successfully updated query parameters or context documents.")
                else:
                    errors.append("Search execution loop did not redirect to a results view layout or append search path parameters.")

        except Exception as e:
            errors.append(f"Search lookup module verification path execution dropped: {str(e)}")

        return {
            "success": success,
            "errors": errors,
            "messages": messages,
            "timings": time.time() - start_time
        }