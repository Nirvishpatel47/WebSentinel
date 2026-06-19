"""
scanner.py
Page scanning, form discovery, and field metadata extraction.
Extends original get_field_info and adds support for select options,
radio/checkbox groups, and basic standalone field detection.
"""

from typing import List, Dict, Any, Optional
from playwright.async_api import Page, Locator

from classifier import classify_field


async def get_field_info(field: Locator) -> Dict[str, Any]:
    """
    Extract comprehensive metadata for a form field.
    Extends the original implementation with select options and group info.
    """
    try:
        tag = await field.evaluate("el => el.tagName.toLowerCase()")
        field_id = await field.get_attribute("id")
        name = await field.get_attribute("name")
        ftype = await field.get_attribute("type")
        placeholder = await field.get_attribute("placeholder")
        required = await field.get_attribute("required") is not None
        aria_label = await field.get_attribute("aria-label")
        disabled = await field.evaluate("el => el.disabled || el.hasAttribute('disabled')")
        readonly = await field.evaluate("el => el.readOnly || el.hasAttribute('readonly')")

        label_text = None
        if field_id:
            page = field.page
            try:
                label = page.locator(f'label[for="{field_id}"]')
                if await label.count() > 0:
                    label_text = await label.first.text_content()
            except Exception:
                pass

        # For select: extract options
        options = []
        if tag == "select":
            try:
                opt_elements = await field.locator("option").all()
                for opt in opt_elements:
                    opt_val = await opt.get_attribute("value")
                    opt_text = await opt.text_content()
                    options.append({
                        "value": opt_val,
                        "text": (opt_text or "").strip()
                    })
            except Exception:
                pass

        # For radio/checkbox: group name (already have 'name')
        group_name = name if ftype in ["radio", "checkbox"] else None

        return {
            "tag": tag,
            "type": ftype,
            "name": name,
            "id": field_id,
            "placeholder": placeholder,
            "required": required,
            "aria_label": aria_label,
            "label": label_text,
            "disabled": disabled,
            "readonly": readonly,
            "options": options if options else None,
            "group_name": group_name
        }
    except Exception as e:
        return {
            "tag": "unknown",
            "type": None,
            "name": None,
            "id": None,
            "placeholder": None,
            "required": False,
            "aria_label": None,
            "label": None,
            "disabled": False,
            "readonly": False,
            "options": None,
            "group_name": None,
            "error": str(e)
        }


async def find_forms(page: Page) -> List[Locator]:
    """Return list of form locators on the page."""
    forms = page.locator("form")
    count = await forms.count()
    return [forms.nth(i) for i in range(count)]


async def find_standalone_fields(page: Page) -> List[Locator]:
    """
    Find input/textarea/select elements that are NOT inside any <form> tag.
    Useful for pages with loose form controls (rare but happens).
    """
    # This is a simplified version: all visible inputs not in form
    # For production, a more robust CSS :not(form *) or JS filter would be better.
    all_fields = page.locator("input, textarea, select")
    standalone = []
    try:
        count = await all_fields.count()
        for i in range(count):
            fld = all_fields.nth(i)
            # Check if ancestor is form
            try:
                parent_form = fld.locator("xpath=ancestor::form")
                if await parent_form.count() == 0:
                    standalone.append(fld)
            except Exception:
                standalone.append(fld)  # Assume standalone if check fails
    except Exception:
        pass
    return standalone


async def scan_page_for_forms(page: Page) -> List[Dict[str, Any]]:
    """
    Main scanning function.
    Returns list of form metadata dicts with fields.
    Each dict: {"form_index": , "locator": , "field_count": , "fields": [...] }
    """
    forms_data = []
    forms = await find_forms(page)

    for idx, form in enumerate(forms):
        fields_locator = form.locator("input, textarea, select")
        field_count = await fields_locator.count()

        fields_info = []
        for f_idx in range(field_count):
            fld = fields_locator.nth(f_idx)
            info = await get_field_info(fld)
            field_type = classify_field(info)
            info["classified_type"] = field_type
            fields_info.append(info)

        forms_data.append({
            "form_index": idx,
            "locator": form,
            "field_count": field_count,
            "fields": fields_info
        })

    # Fallback: if no forms found, treat standalone fields as one virtual form (index -1)
    if not forms_data:
        standalone = await find_standalone_fields(page)
        if standalone:
            fields_info = []
            for fld in standalone:
                info = await get_field_info(fld)
                field_type = classify_field(info)
                info["classified_type"] = field_type
                fields_info.append(info)

            forms_data.append({
                "form_index": -1,  # Virtual form
                "locator": None,   # No single form locator
                "field_count": len(fields_info),
                "fields": fields_info,
                "is_standalone": True
            })

    return forms_data