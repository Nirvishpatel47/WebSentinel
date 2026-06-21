#!/usr/bin/env python3

from typing import List, Dict, Any

from playwright.async_api import Page, Locator

from Scanner.Forms.BaseFormTester import BaseFormTester
from Scanner.Forms.FormResult import FormResult


class ContactFormTester(BaseFormTester):
    """
    Tests contact and support forms.
    """

    async def test(
        self,
        page: Page,
        form_locator: Locator,
        fields: List[Dict[str, Any]]
    ) -> FormResult:

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

                if field_type == "email":
                    await locator.fill("test_sentinel@example.com")

                elif field_type == "tel" or "phone" in field_name:
                    await locator.fill("+1234567890")

                elif "name" in field_name:
                    await locator.fill("John WebSentinel")

                elif "company" in field_name:
                    await locator.fill("WebSentinel")

                elif field_type == "textarea" or "message" in field_name:
                    await locator.fill(
                        "Automated contact form verification from WebSentinel."
                    )

                elif field_type in ["text", "textarea"]:
                    await locator.fill("WebSentinel Test")

            result.messages.append(
                "Fields populated successfully."
            )

            initial_url = page.url

            submit_btn = form_locator.locator(
                """
                button[type='submit'],
                input[type='submit'],
                button:has-text('Submit'),
                button:has-text('Send')
                """
            ).first

            if await submit_btn.count() > 0 and await submit_btn.is_visible():

                result.messages.append(
                    "Submitting contact form."
                )

                await submit_btn.click(
                    timeout=2000,
                    no_wait_after=True
                )

                await page.wait_for_timeout(1000)

            else:
                result.errors.append(
                    "Submit button not found."
                )

            html = (await page.content()).lower()

            success_keywords = [
                "thank you",
                "thanks",
                "submitted",
                "success",
                "received",
                "message sent",
                "we'll contact",
                "has been sent"
            ]

            if (
                page.url != initial_url
                or any(keyword in html for keyword in success_keywords)
            ):
                result.success = True

                result.messages.append(
                    "Submission confirmed."
                )

            else:
                result.errors.append(
                    "No visible success indicator detected."
                )

        except Exception as e:
            result.errors.append(str(e))

        return self.finish_result(result, start_time)