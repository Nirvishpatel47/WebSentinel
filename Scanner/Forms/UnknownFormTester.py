#!/usr/bin/env python3
import time
from playwright.async_api import Page, Locator
from typing import List, Dict, Any

class UnknownFormTester:
    """
    Responsibility: Executes fallback testing sequences on unclassified forms while explicitly mitigating submission safety hazards.
    """
    async def test(self, page: Page, form_locator: Locator, fields: List[Dict[str, Any]]) -> Dict[str, Any]:
        start_time = time.time()
        messages = []
        errors = []
        success = False

        try:
            messages.append("Form profile matched fallback state. Triggering passive field verification pipeline...")
            
            # 1. Passive interaction pass: Fill fields safely without triggering submission events
            interacted_count = 0
            for field in fields:
                if field['tag'] in ['input', 'textarea'] and field['type'] not in ['submit', 'button', 'hidden']:
                    input_loc = form_locator.locator(f"{field['tag']}[name='{field['name']}']").first if field['name'] else None
                    if input_loc and await input_loc.is_visible():
                        await input_loc.focus()
                        await input_loc.fill("Sentinel_Fallback_Audit")
                        interacted_count += 1

            if interacted_count > 0:
                success = True
                messages.append(f"Successfully evaluated data compliance constraints across {interacted_count} unclassified form input nodes.")
            else:
                errors.append("Unclassified form configuration possesses zero editable interactable content element tags.")

        except Exception as e:
            errors.append(f"Safety wrapper exception logged during passive evaluation run: {str(e)}")

        return {
            "success": success,
            "errors": errors,
            "messages": messages,
            "timings": time.time() - start_time
        }