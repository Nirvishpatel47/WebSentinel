#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright, Page
from typing import List, Dict

class FormExtractor:
    async def extract_forms(self, page: Page) -> List[Dict]:
        """Collects structural definitions of interactable form containers and loose form elements."""
        return await page.evaluate("""
        () => {
            const extractedForms = [];
            
            // 1. Process explicit standard HTML forms
            const standardForms = [...document.querySelectorAll('form')];
            const processedInputs = new Set();

            standardForms.forEach(f => {
                const inputElements = [...f.querySelectorAll('input, select, textarea, button')];
                inputElements.forEach(i => processedInputs.add(i));

                extractedForms.push({
                    type: 'standard_form',
                    action: f.getAttribute('action') || '',
                    method: (f.getAttribute('method') || 'GET').toUpperCase(),
                    inputs: inputElements.map(i => ({
                        tag: i.tagName.toLowerCase(),
                        type: i.getAttribute('type') || i.tagName.toLowerCase(),
                        name: i.getAttribute('name') || i.getAttribute('id') || '',
                        required: i.hasAttribute('required'),
                        value: i.value || i.getAttribute('value') || '',
                        options: i.tagName.toLowerCase() === 'select' ? [...i.options].map(o => o.value) : []
                    }))
                });
            });

            // 2. Process loose, standalone inputs common in modern SPAs (React/Vue/Angular)
            const allInputs = [...document.querySelectorAll('input, select, textarea')];
            const looseInputs = allInputs.filter(i => !processedInputs.has(i));

            if (looseInputs.length > 0) {
                extractedForms.push({
                    type: 'javascript_loose_form',
                    action: window.location.href,
                    method: 'DYNAMIC_JS',
                    inputs: looseInputs.map(i => ({
                        tag: i.tagName.toLowerCase(),
                        type: i.getAttribute('type') || i.tagName.toLowerCase(),
                        name: i.getAttribute('name') || i.getAttribute('id') || '',
                        required: i.hasAttribute('required'),
                        value: i.value || i.getAttribute('value') || '',
                        options: i.tagName.toLowerCase() === 'select' ? [...i.options].map(o => o.value) : []
                    }))
                });
            }

            return extractedForms;
        }
        """)


if __name__ == "__main__":
    async def test_form_extractor():
        TARGET_URL = "http://127.0.0.1:5501/TESTING/Website-5/contact.html"
        extractor = FormExtractor()

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            print(f"Navigating browser to target form sandbox: {TARGET_URL}")
            await page.goto(TARGET_URL, wait_until="domcontentloaded")
            
            detected_forms = await extractor.extract_forms(page)
            
            print(detected_forms)
                    
            await browser.close()
    asyncio.run(test_form_extractor())