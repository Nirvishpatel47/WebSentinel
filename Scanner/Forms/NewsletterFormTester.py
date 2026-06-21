#!/usr/bin/env python3

from typing import List, Dict, Any

from playwright.async_api import Page, Locator

from Scanner.Forms.BaseFormTester import BaseFormTester
from Scanner.Forms.FormResult import FormResult


class NewsletterFormTester(BaseFormTester):
    """
    Tests newsletter subscription forms.
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

            email_locator = None

            for field in fields:

                field_type = field.get("type", "")
                field_name = field.get("name", "").lower()

                if (
                    field_type == "email"
                    or "email" in field_name
                ):
                    email_locator = self.get_field_locator(
                        form_locator,
                        field
                    )
                    break

            if (
                email_locator is not None
                and await email_locator.is_visible()
            ):

                await email_locator.fill(
                    "sentinel_subscribe_test@example.com"
                )

                result.messages.append(
                    "Email populated."
                )

            else:
                result.errors.append(
                    "Email field not found."
                )

            submit_button = form_locator.locator(
                """
                button[type='submit'],
                input[type='submit'],
                button:has-text('Subscribe'),
                button:has-text('Join')
                """
            ).first

            if (
                await submit_button.count() > 0
                and await submit_button.is_visible()
            ):

                await submit_button.click(
                    timeout=2000,
                    no_wait_after=True
                )

                await page.wait_for_timeout(800)

                result.messages.append(
                    "Newsletter submit triggered."
                )

            html = (await page.content()).lower()

            success_keywords = [
                "subscribed",
                "joined",
                "success",
                "welcome",
                "newsletter",
                "confirm"
            ]

            failure_keywords = [
                "error",
                "invalid",
                "failed"
            ]

            if (
                any(x in html for x in success_keywords)
                and not any(x in html for x in failure_keywords)
            ):

                result.success = True

                result.messages.append(
                    "Newsletter verification passed."
                )

            else:
                result.errors.append(
                    "No successful subscription confirmation detected."
                )

        except Exception as e:
            result.errors.append(str(e))

        return self.finish_result(result, start_time)