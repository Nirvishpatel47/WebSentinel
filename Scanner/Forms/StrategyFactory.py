#!/usr/bin/env python3

from typing import Any

from Scanner.Forms.ContactFormTester import ContactFormTester
from Scanner.Forms.NewsletterFormTester import NewsletterFormTester
from Scanner.Forms.LoginFormTester import LoginFormTester
from Scanner.Forms.SearchFormTester import SearchFormTester
from Scanner.Forms.UnknownFormTester import UnknownFormTester


class StrategyFactory:
    """
    Responsibility:
        Return the correct tester for a classified form type.
    """

    def __init__(self):
        self.strategy_map = {
            "CONTACT": ContactFormTester(),
            "NEWSLETTER": NewsletterFormTester(),
            "LOGIN": LoginFormTester(),
            "SEARCH": SearchFormTester(),

            "BOOKING": UnknownFormTester(),
            "QUOTE": UnknownFormTester(),
            "UNKNOWN": UnknownFormTester()
        }

    def get_tester(self, form_type: str) -> Any:
        """
        Returns the tester instance associated with the form type.
        """
        return self.strategy_map.get(form_type, self.strategy_map["UNKNOWN"])