#!/usr/bin/env python3

from typing import List, Dict, Any

from playwright.async_api import Page, Locator

from Scanner.Forms.BaseFormTester import BaseFormTester
from Scanner.Forms.FormResult import FormResult


class UnknownFormTester(BaseFormTester):
    """
    Safely evaluates unknown forms without submitting them.
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

            interacted_count = 0

            for field in fields:

                field_type = field.get("type", "")
                tag = field.get("tag", "")

                if (
                    tag not in ["input", "textarea"]
                    or field_type in [
                        "submit",
                        "button",
                        "hidden"
                    ]
                ):
                    continue

                locator = self.get_field_locator(
                    form_locator,
                    field
                )

                if locator is None:
                    continue

                if not await locator.is_visible():
                    continue

                await locator.focus()

                if field_type == "email":
                    await locator.fill(
                        "test@example.com"
                    )

                elif field_type == "tel":
                    await locator.fill(
                        "+1234567890"
                    )

                else:
                    await locator.fill(
                        "Sentinel_Fallback_Audit"
                    )

                interacted_count += 1

            if interacted_count > 0:

                result.success = True

                result.messages.append(
                    f"Validated {interacted_count} editable fields."
                )

            else:

                result.errors.append(
                    "No editable inputs found."
                )

        except Exception as e:
            result.errors.append(str(e))

        return self.finish_result(
            result,
            start_time
        )