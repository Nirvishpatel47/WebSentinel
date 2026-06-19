"""
submitter.py
Submit button detection and form submission logic.
Extends original find_submit_button with more keywords and heuristics.
"""

from typing import Optional, List
from playwright.async_api import Locator, Page

# Common submit-related keywords (case-insensitive match on text)
SUBMIT_KEYWORDS = [
    "submit", "send", "contact", "register", "sign up", "signup",
    "continue", "apply", "save", "create account", "join", "get started",
    "next", "proceed", "confirm", "book", "order", "buy", "purchase",
    "login", "log in", "sign in", "subscribe", "download", "request"
]


async def find_submit_button(form: Locator) -> Optional[Locator]:
    """
    Find the most likely submit button inside a form.
    Returns the Locator or None.
    Preserves and extends original logic.
    """
    if not form:
        return None

    # Priority selectors
    selectors = [
        'button[type="submit"]',
        'input[type="submit"]',
        'button[type="button"]',  # Sometimes used as submit
        'button',                 # Generic fallback
        'input[type="button"]'
    ]

    for selector in selectors:
        try:
            buttons = form.locator(selector)
            count = await buttons.count()

            for i in range(count):
                button = buttons.nth(i)

                try:
                    # Get text content
                    text = (await button.text_content() or "").strip().lower()
                    button_type = (await button.get_attribute("type") or "").lower()

                    # Strong match: explicit submit type
                    if button_type == "submit":
                        return button

                    # Keyword match in visible text or value attribute
                    value_attr = (await button.get_attribute("value") or "").lower()
                    if any(word in text or word in value_attr for word in SUBMIT_KEYWORDS):
                        return button

                    # Also check aria-label or title
                    aria = (await button.get_attribute("aria-label") or "").lower()
                    title = (await button.get_attribute("title") or "").lower()
                    if any(word in aria or word in title for word in SUBMIT_KEYWORDS):
                        return button

                except Exception:
                    continue
        except Exception:
            continue

    # Last resort: any button or input that looks clickable inside form
    try:
        any_buttons = form.locator('button, input[type="button"], input[type="submit"]')
        if await any_buttons.count() > 0:
            return any_buttons.first
    except Exception:
        pass

    return None


async def submit_form(form: Locator, submit_btn: Optional[Locator] = None, timeout: int = 5000) -> bool:
    """
    Click the submit button (or fallback to form submit).
    Returns True if click/submit was attempted without immediate error.
    """
    try:
        if submit_btn:
            await submit_btn.click(timeout=timeout)
            return True
        else:
            # Fallback: submit the form directly via JS
            await form.evaluate("form => form.submit()")
            return True
    except Exception as e:
        print(f"[submitter] Submit failed: {str(e)[:120]}")
        return False


async def wait_after_submit(page: Page, wait_time: int = 3000) -> None:
    """Wait for page to settle after submission."""
    try:
        await page.wait_for_timeout(wait_time)
        # Optionally wait for network idle, but can be flaky on some sites
        # await page.wait_for_load_state("networkidle", timeout=5000)
    except Exception:
        pass