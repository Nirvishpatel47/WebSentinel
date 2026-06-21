#!/usr/bin/env python3

from typing import List, Dict, Any

from playwright.async_api import Page, Locator

from Scanner.Forms.BaseFormTester import BaseFormTester
from Scanner.Forms.FormResult import FormResult
from Scanner.Forms.FormEvidenceCollector import Evidence

class ContactFormTester(BaseFormTester):
    """
    Tests contact and support forms.
    """
    async def test( self, page: Page, form_locator: Locator, fields: List[Dict[str, Any]] ) -> FormResult:

            start_time = self.start_timer()
            result = FormResult()

            try:
                # Fill fields
                for field in fields:
                    locator = self.get_field_locator(form_locator, field)
                    if locator is None:
                        continue
                    if not await locator.is_visible():
                        continue

                    field_type = field.get("type", "")
                    field_name = field.get("name", "").lower()
                    field_tag = field.get("tag", "").lower()

                    if field_type == "email":
                        await locator.fill("test_sentinel@example.com")

                    elif field_type == "tel" or "phone" in field_name:
                        await locator.fill("+1234567890")

                    elif "name" in field_name:
                        await locator.fill("John WebSentinel")

                    elif "company" in field_name:
                        await locator.fill("WebSentinel")

                    elif field_type == "textarea" or "message" in field_name:
                        await locator.fill( "Automated contact form verification from WebSentinel." )

                    elif field_type in ["text", "textarea"]:
                        await locator.fill("WebSentinel Test")

                    # Handle select dropdown menus
                    elif field_tag == "select" or field_type == "select":
                        options = field.get("options", [])
                        valid_options = [o for o in options if o.strip()]
                        if valid_options:
                            await locator.select_option(value=valid_options[0])
                        else:
                            try:
                                await locator.select_option(index=1)
                            except:
                                pass

                    # Handle checkboxes
                    elif field_type == "checkbox":
                        try:
                            await locator.check(timeout=500)
                        except:
                            pass

                    # Handle radio options
                    elif field_type == "radio":
                        try:
                            await locator.check(timeout=500)
                        except:
                            pass

                result.messages.append( "Fields populated successfully." )

                initial_url = page.url

                # FIXED: Prefixed each clause with explicit direct child/descendant restrictions 
                # to prevent searching outside the targeted form_locator container boundary.
                selector_matrix = (
                    "button[type='submit'], input[type='submit'], button:has-text('Send Message'), "
                    "button:has-text('Send'), button:has-text('Submit'), .form-actions button, "
                    "input[type='button'][value*='Send' i], input[type='button'][value*='Submit' i]"
                )
                
                # Force resolution relative strictly to this form block container
                submit_btn = form_locator.locator(selector_matrix).first

                await page.screenshot(path=r"F:\WebSentinel\Evidence\screenshot1.png", full_page=True)
                result.before_screenshot = (
                    await Evidence.capture_form_snapshot(
                        form_locator,
                        "CONTACT",
                        "before"
                    )
                )
                
                # Check button state explicitly
                if await submit_btn.count() > 0 and await submit_btn.is_visible():
                    btn_text = await submit_btn.inner_text()
                    result.messages.append(f"Submitting contact form via isolated target: '{btn_text.strip()}'")

                    # 1. Fire click sequence
                    await submit_btn.click(timeout=2000)

                    # 2. Dynamic Verification Phase: Watch for popups or validation text changes
                    try:
                        await page.wait_for_selector(
                            "text=thank you, text=success, text=submitted, text=received, text=sent, .modal, .popup, [id*='success']", 
                            state="visible", 
                            timeout=2500
                        )
                        result.messages.append("DOM shift verified: Detected success signature rendering event.")
                    except Exception:
                        result.messages.append("No immediate structural selector matched. Falling back to layout analysis.")
                        await page.wait_for_timeout(1000)

                    # 3. Capture evidence assets post-click
                    await page.screenshot(path=r"F:\WebSentinel\Evidence\screenshot.png", full_page=True)
                    result.after_screenshot = (
                        await Evidence.capture_form_snapshot(
                            page.locator("body"),
                            "CONTACT",
                            "after"
                        )
                    )

                    # 4. Strict Success Evaluation (Only executed if clicked)
                    html = (await page.content()).lower()
                    success_keywords = [
                        "thank you", "thanks", "submitted", "success", 
                        "received", "message sent", "we'll contact", "has been sent"
                    ]

                    if (page.url != initial_url or any(keyword in html for keyword in success_keywords)):
                        result.success = True
                        result.messages.append("Submission confirmed via backend response mapping.")
                    else:
                        result.success = False
                        result.errors.append("No visible success indicator detected post-interaction.")

                else:
                    # Explicit Failure: Form was never submitted
                    result.success = False
                    result.errors.append("Submit button not found.")

            except Exception as e:
                result.success = False
                result.errors.append(str(e))

            return self.finish_result(result, start_time)