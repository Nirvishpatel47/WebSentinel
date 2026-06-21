#!/usr/bin/env python3

from typing import List, Dict, Any

from playwright.async_api import Page, Locator

from Scanner.Forms.BaseFormTester import BaseFormTester
from Scanner.Forms.FormResult import FormResult


class SearchFormTester(BaseFormTester):
    """
    Verifies search functionality.
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

            search_input = None

            for field in fields:

                field_name = field.get("name", "").lower()
                field_type = field.get("type", "")

                if (
                    field_type in ["text", "search"]
                    or field_name in ["q", "search", "query"]
                ):
                    search_input = self.get_field_locator(
                        form_locator,
                        field
                    )
                    break

            if (
                search_input is not None
                and await search_input.is_visible()
            ):

                await search_input.fill(
                    "WebSentinel_Validation_Query"
                )

                result.messages.append(
                    "Search query populated."
                )

                await search_input.press("Enter")

                await page.wait_for_timeout(1500)

                html = (
                    await page.content()
                ).lower()

                url = page.url.lower()

                if (
                    "search" in url
                    or "query" in url
                    or "websentinel_validation_query" in html
                ):

                    result.success = True

                    result.messages.append(
                        "Search execution verified."
                    )

                else:
                    result.errors.append(
                        "No search result indicators detected."
                    )

            else:
                result.errors.append(
                    "Search input not found."
                )

        except Exception as e:
            result.errors.append(str(e))

        return self.finish_result(
            result,
            start_time
        )