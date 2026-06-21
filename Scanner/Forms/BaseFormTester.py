#!/usr/bin/env python3
import time
from typing import Dict, Any, Optional

from playwright.async_api import Locator

from Scanner.Forms.FormResult import FormResult


class BaseFormTester:
    """
    Common utilities shared by all form testers.
    """

    def start_timer(self) -> float:
        return time.time()

    def finish_result(self, result: FormResult, start_time: float) -> FormResult:
        result.timings = time.time() - start_time
        return result

    def get_field_locator( self, form_locator: Locator, field: Dict[str, Any] ) -> Optional[Locator]:

        if field.get("name"): return form_locator.locator( f"{field['tag']}[name='{field['name']}']" ).first

        if field.get("id"): return form_locator.locator( f"#{field['id']}" ).first

        if field.get("placeholder"): return form_locator.get_by_placeholder( field["placeholder"] ).first

        return None