"""
filler.py
Form field filling logic.
Extends original fill_field to support HTML5 controls: radio, checkbox, select, date, file, etc.
Preserves original behavior for text inputs and textareas.
"""

import asyncio
from typing import Dict, Any, Optional
from playwright.async_api import Locator, Page

from data_generator import get_test_value, get_dummy_file_path, should_fill_field


async def fill_field(locator: Locator, field_type: str, field_info: Optional[Dict[str, Any]] = None) -> bool:
    """
    Fill a single form field intelligently based on its type.
    Returns True if fill succeeded, False otherwise.
    """
    if not locator:
        return False

    if field_info and not should_fill_field(field_info):
        return False

    value = get_test_value(field_type, field_info)

    try:
        tag = await locator.evaluate("el => el.tagName.toLowerCase()")
        ftype = (field_info.get("type") if field_info else None) or await locator.get_attribute("type") or ""
        ftype = ftype.lower()

        # Skip hidden
        if ftype == "hidden":
            return False

        # Check disabled/readonly via JS (more reliable)
        is_disabled = await locator.evaluate("el => el.disabled || el.readOnly || el.hasAttribute('disabled') || el.hasAttribute('readonly')")
        if is_disabled and not (field_info and field_info.get("required")):
            return False

        # === INPUT types ===
        if tag == "input":
            if ftype in ["text", "email", "password", "tel", "url", "number", "search"]:
                if value is not None:
                    await locator.fill(str(value))
                return True

            if ftype in ["date", "datetime-local"]:
                if value:
                    await locator.fill(str(value))
                return True

            if ftype == "checkbox":
                # Check the box (especially if required)
                is_checked = await locator.is_checked()
                if not is_checked:
                    await locator.check()
                return True

            if ftype == "radio":
                # For radio, we usually want to select it (first in group will be handled by caller or here)
                is_checked = await locator.is_checked()
                if not is_checked:
                    await locator.check()
                return True

            if ftype == "file":
                dummy_path = get_dummy_file_path()
                if dummy_path:
                    await locator.set_input_files(dummy_path)
                    # Optionally clean up later, but for QA test leave it
                    return True
                return False  # No file available

            if ftype in ["submit", "button", "reset"]:
                return False  # Not for filling

            # Fallback for other input types
            if value is not None:
                await locator.fill(str(value))
            return True

        # === TEXTAREA ===
        if tag == "textarea":
            if value is not None:
                await locator.fill(str(value))
            return True

        # === SELECT ===
        if tag == "select":
            # Choose first valid option (skip placeholder / empty / disabled)
            try:
                options = await locator.locator("option").all()
                for opt in options:
                    opt_value = await opt.get_attribute("value") or ""
                    opt_text = (await opt.text_content() or "").strip().lower()
                    disabled = await opt.evaluate("el => el.disabled")

                    if opt_value and opt_value.lower() not in ["", "placeholder", "select", "choose"] and not disabled:
                        await locator.select_option(value=opt_value)
                        return True

                # Fallback: select by index 1 if exists
                option_count = await locator.locator("option").count()
                if option_count > 1:
                    await locator.select_option(index=1)
                    return True
            except Exception:
                pass
            return False

        return False

    except Exception as e:
        # Silent fail per field - caller can log
        print(f"[filler] Fill failed for {field_type}: {str(e)[:100]}")
        return False


async def fill_radio_group(page: Page, name: str, form_locator: Optional[Locator] = None) -> bool:
    """
    Select the first enabled radio button in a group with the given name.
    Useful when processing fields in order and wanting to ensure one is selected.
    """
    try:
        selector = f'input[type="radio"][name="{name}"]'
        if form_locator:
            radios = form_locator.locator(selector)
        else:
            radios = page.locator(selector)

        count = await radios.count()
        for i in range(count):
            radio = radios.nth(i)
            disabled = await radio.evaluate("el => el.disabled")
            if not disabled:
                await radio.check()
                return True
        return False
    except Exception:
        return False


async def fill_checkbox_group(page: Page, name: str, form_locator: Optional[Locator] = None, check_all: bool = False) -> int:
    """
    Check all (or first) enabled checkboxes in a group.
    Returns number checked.
    """
    checked = 0
    try:
        selector = f'input[type="checkbox"][name="{name}"]'
        if form_locator:
            cbs = form_locator.locator(selector)
        else:
            cbs = page.locator(selector)

        count = await cbs.count()
        for i in range(count):
            cb = cbs.nth(i)
            disabled = await cb.evaluate("el => el.disabled")
            if not disabled:
                is_checked = await cb.is_checked()
                if not is_checked:
                    await cb.check()
                    checked += 1
                if not check_all:
                    break  # Only first one
        return checked
    except Exception:
        return checked