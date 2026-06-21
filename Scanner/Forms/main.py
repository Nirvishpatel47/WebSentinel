#!/usr/bin/env python3
import asyncio
import json
from playwright.async_api import async_playwright
from Scanner.Forms.FormManager import FormManager

async def test_full_pipeline():
    TARGET_URL = "http://127.0.0.1:5500/tests/Website-5/contact.html"
    manager = FormManager()

    async with async_playwright() as p:
        print(f"Launching headless sandbox for central FormManager verification...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto(TARGET_URL, wait_until="networkidle")
        
        # Execute the orchestrated data workflow pipeline
        audit_report = await manager.process_page_forms(page, TARGET_URL)
        
        print("\n" + "="*50)
        print("📋 ORCHESTRATION PIPELINE INTEGRATION RUN OUTPUT")
        print("="*50)
        print(json.dumps(audit_report, indent=4))
        print("="*50 + "\n")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_full_pipeline())