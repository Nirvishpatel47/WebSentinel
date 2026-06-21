#!/usr/bin/env python3

from typing import List, Dict, Any

from playwright.async_api import Page, Locator

from Scanner.Forms.BaseFormTester import BaseFormTester
from Scanner.Forms.FormResult import FormResult


class LoginFormTester(BaseFormTester):
    """
    Verifies login form structure and validation behavior.
    Does NOT attempt real authentication.
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

            for field in fields:

                locator = self.get_field_locator(
                    form_locator,
                    field
                )

                if locator is None:
                    continue

                if not await locator.is_visible():
                    continue

                field_type = field.get("type", "")
                field_name = field.get("name", "").lower()

                if field_type == "password":
                    await locator.fill(
                        "Sentinel_Protected_Pass_99!"
                    )

                elif (
                    "user" in field_name
                    or "mail" in field_name
                    or field_type == "email"
                ):
                    await locator.fill(
                        "sentinel_audit_user@test.org"
                    )

            result.messages.append(
                "Authentication inputs populated."
            )

            submit_btn = form_locator.locator(
                """
                button[type='submit'],
                input[type='submit'],
                button:has-text('Log'),
                button:has-text('Sign')
                """
            ).first

            if (
                await submit_btn.count() > 0
                and await submit_btn.is_visible()
            ):

                await submit_btn.click(
                    timeout=2000,
                    no_wait_after=True
                )

                await page.wait_for_timeout(1000)

                result.success = True

                result.messages.append(
                    "Login form accepted interaction."
                )

            else:
                result.errors.append(
                    "Login submit control not found."
                )

        except Exception as e:
            result.errors.append(str(e))

        return self.finish_result(
            result,
            start_time
        )