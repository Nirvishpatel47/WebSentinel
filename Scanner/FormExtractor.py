#!/usr/bin/env python3
from playwright.async_api import Page
from typing import List, Dict

class FormExtractor:
    async def extract_forms(self, page: Page) -> List[Dict]:
        """Collects structural definitions of interactable form containers."""
        return await page.evaluate("""
        () => [...document.querySelectorAll('form')].map(f => ({
            action: f.getAttribute('action') || '',
            method: (f.getAttribute('method') || 'GET').toUpperCase(),
            inputs: [...f.querySelectorAll('input, select, textarea')].map(i => ({
                type: i.getAttribute('type') || i.tagName.toLowerCase(),
                name: i.getAttribute('name') || '',
                required: i.hasAttribute('required')
            }))
        }))
        """)