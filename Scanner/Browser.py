#!/usr/bin/env python3
import os
import re
from playwright.async_api import async_playwright, BrowserContext, Page

class BrowserManager:
    def __init__(self, screenshots_dir: str = "./proofs"):
        self.screenshots_dir = screenshots_dir
        self.playwright = None
        self.browser = None
        self.context = None

    async def init_session(self) -> BrowserContext:
        """Spawns an isolated Chromium instance with custom headers."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 WebSentinel/3.0"
        )
        return self.context

    def safe_filename(self, text: str) -> str:
        return re.sub(r'[<>:"/\\\\|?*]', '_', text)

    async def take_screenshot(self, page: Page, url: str, code: int):
        if not self.screenshots_dir:
            return
        os.makedirs(self.screenshots_dir, exist_ok=True)
        path = os.path.join(self.screenshots_dir, f"{self.safe_filename(url)}_{code}.png")
        try:
            await page.screenshot(path=path, full_page=True)
            print(f"📸 Screenshot saved -> {path}")
        except Exception as e:
            print(f"⚠️ Screenshot failed: {e}")

    async def close_session(self):
        if self.context: await self.context.close()
        if self.browser: await self.browser.close()
        if self.playwright: await self.playwright.stop()