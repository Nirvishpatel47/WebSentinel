"""
detector.py
Success / failure detection after form submission.
Extends original detect_result with more signals, confidence scoring,
modal/alert detection, and better heuristics.
"""

from typing import Dict, Any, List, Optional
from playwright.async_api import Page

# Success indicators (text content match, case-insensitive)
SUCCESS_PATTERNS = [
    "thank you", "thanks", "success", "submitted", "message sent",
    "form submitted", "received", "completed", "confirmation",
    "we have received", "your request has been", "successfully",
    "thank you for", "we'll get back", "request submitted"
]

# Error / validation failure indicators
ERROR_PATTERNS = [
    "required", "invalid", "error", "please enter", "field is required",
    "please fill", "cannot be empty", "must be", "incorrect",
    "failed", "problem", "try again", "something went wrong"
]

# Additional success signals in common success pages / modals
SUCCESS_MODAL_SELECTORS = [
    ".success", ".thank-you", ".confirmation", ".modal-success",
    "[class*='success']", "[class*='thank']", "[role='alert']",
    ".alert-success", "#success", "#thankyou"
]


async def detect_result(page: Page, old_url: str, form_locator: Optional[Any] = None) -> Dict[str, Any]:
    """
    Detect submission outcome using multiple signals.
    Returns dict with success, confidence, reason, url_changed, etc.
    """
    result = {
        "success": False,
        "url_changed": False,
        "success_text": None,
        "error_text": None,
        "confidence": 0.0,
        "reason": "no clear signal",
        "modal_detected": False,
        "form_disappeared": False
    }

    try:
        current_url = page.url
        if current_url != old_url:
            result["url_changed"] = True

        # Get page text content (lowercase for matching)
        try:
            content = (await page.text_content("body") or "").lower()
        except Exception:
            content = ""

        # Signal 1: Success text patterns
        for pattern in SUCCESS_PATTERNS:
            if pattern in content:
                result["success"] = True
                result["success_text"] = pattern
                result["confidence"] = 0.9
                result["reason"] = f"success text detected: '{pattern}'"
                return result

        # Signal 2: Error patterns (only if no success)
        for pattern in ERROR_PATTERNS:
            if pattern in content:
                result["error_text"] = pattern
                result["confidence"] = 0.7
                result["reason"] = f"error/validation text detected: '{pattern}'"
                return result

        # Signal 3: Success modal / alert box
        for selector in SUCCESS_MODAL_SELECTORS:
            try:
                modal = page.locator(selector)
                if await modal.count() > 0:
                    # Check if any is visible
                    for i in range(min(await modal.count(), 5)):
                        m = modal.nth(i)
                        if await m.is_visible():
                            modal_text = (await m.text_content() or "").lower()
                            if any(p in modal_text for p in ["thank", "success", "received", "submitted"]):
                                result["success"] = True
                                result["modal_detected"] = True
                                result["success_text"] = modal_text[:80]
                                result["confidence"] = 0.85
                                result["reason"] = "success modal/alert detected"
                                return result
            except Exception:
                continue

        # Signal 4: Form disappeared (common after successful AJAX submit)
        if form_locator:
            try:
                if await form_locator.count() == 0 or not await form_locator.is_visible():
                    result["form_disappeared"] = True
                    if result["url_changed"]:
                        result["success"] = True
                        result["confidence"] = 0.75
                        result["reason"] = "form disappeared + url changed"
                        return result
                    else:
                        # Still possible success on same page (AJAX)
                        result["success"] = True
                        result["confidence"] = 0.65
                        result["reason"] = "form disappeared after submit"
                        return result
            except Exception:
                pass

        # Signal 5: URL changed significantly (different path)
        if result["url_changed"]:
            # Check if new URL looks like success/confirmation page
            if any(x in current_url.lower() for x in ["success", "thank", "confirm", "complete", "submitted"]):
                result["success"] = True
                result["confidence"] = 0.8
                result["reason"] = "redirected to success-like URL"
                return result
            else:
                # Neutral/possible success
                result["success"] = True
                result["confidence"] = 0.55
                result["reason"] = "url changed after submit"
                return result

        # Default: no strong signal
        if result["url_changed"]:
            result["success"] = True
            result["confidence"] = 0.5
            result["reason"] = "url changed (weak signal)"
        else:
            result["success"] = False
            result["confidence"] = 0.3
            result["reason"] = "no success or error signals detected"

    except Exception as e:
        result["reason"] = f"detection error: {str(e)[:80]}"

    return result


async def check_network_success(page: Page, timeout: int = 5000) -> bool:
    """
    Optional: Listen for successful network responses after submit (advanced).
    Can be used by wrapping submit in a listener.
    Returns True if saw 200/201/202 response.
    Note: This is best-effort and may require context manager in caller.
    """
    # This is a helper; full implementation would use page.on("response")
    # For now, we keep detection simple and text/URL based.
    return False