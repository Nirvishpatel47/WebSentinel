#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright, Page
from typing import List, Dict

#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright, Page, Locator
from typing import List, Dict

class FormExtractor:
    """
    Responsibility: Discover forms and extract structural properties.
    Preserves exact reliability logic while providing locator streams for FormManager orchestration.
    """
    async def locate_forms(self, page: Page) -> List[Locator]:
        """
        Provides the Locator array required by FormManager framework loops.
        """
        locators = []
        try:
            # 1. Grab all standard explicit HTML forms
            standard_forms = await page.locator("form").all()
            locators.extend(standard_forms)

            # 2. Check for loose inputs using your exact logic filter to determine if body container is needed
            has_loose_inputs = await page.evaluate("""
                () => {
                    const standardForms = [...document.querySelectorAll('form')];
                    const processedInputs = new Set();
                    standardForms.forEach(f => {
                        [...f.querySelectorAll('input, select, textarea')].forEach(i => processedInputs.add(i));
                    });
                    const allInputs = [...document.querySelectorAll('input, select, textarea')];
                    const looseInputs = allInputs.filter(i => !processedInputs.has(i));
                    return looseInputs.length > 0;
                }
            """)

            if has_loose_inputs:
                # Add the body element to act as the locator shell for loose interactive layouts
                locators.append(page.locator("body"))
        except Exception:
            pass
        return locators

    async def extract_forms(self, page: Page) -> List[Dict]:
        extracted_forms = []

        form_locators = await page.locator("form").all()

        for form_locator in form_locators:

            form_data = await form_locator.evaluate("""
            (form) => {

                function getLabel(element) {
                    return (
                        element.labels?.[0]?.innerText?.trim() ||
                        element.getAttribute('placeholder') ||
                        element.getAttribute('aria-label') ||
                        ''
                    );
                }

                function extractField(element) {

                    return {
                        tag: element.tagName.toLowerCase(),
                        type: element.getAttribute('type') || element.tagName.toLowerCase(),
                        name: element.getAttribute('name') || '',
                        id: element.id || '',
                        placeholder: element.getAttribute('placeholder') || '',
                        label: getLabel(element),
                        required: element.hasAttribute('required')
                    };

                }

                const controls = [
                    ...form.querySelectorAll(
                        'input, textarea, select, button'
                    )
                ];

                return {

                    action: form.getAttribute('action') || '',

                    method: (
                        form.getAttribute('method') || 'GET'
                    ).toUpperCase(),

                    fields: controls.map(extractField)

                };
            }
            """)

            form_data["locator"] = form_locator

            extracted_forms.append(form_data)

        return extracted_forms
    
if __name__ == "__main__":
    async def test_form_extractor():
        TARGET_URL = "http://127.0.0.1:5500/tests/Website-5/contact.html"
        extractor = FormExtractor()

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            print(f"Navigating browser to target form sandbox: {TARGET_URL}")
            await page.goto(TARGET_URL, wait_until="domcontentloaded")
            
            # Verify both contracts are satisfied perfectly
            locators = await extractor.locate_forms(page)
            data_spec = await extractor.extract_forms(page)
            
            print(locators)
            print("\n\n\n\n\n" , data_spec)
                    
            await browser.close()
    asyncio.run(test_form_extractor())

