#!/usr/bin/env python3
import logging
from typing import Any

# Fallback imports assuming files will follow your design directory schema
# (Replace with your actual import locations as you create the tester scripts)
from Scanner.Forms.ContactFormTester import ContactFormTester
from Scanner.Forms.NewsletterFormTester import NewsletterFormTester
from Scanner.Forms.LoginFormTester import LoginFormTester
from Scanner.Forms.SearchFormTester import SearchFormTester
from Scanner.Forms.UnknownFormTester import UnknownFormTester

logger = logging.getLogger(__name__)


class StrategyFactory:
    """
    Returns the designated automated form tester based on the identified FormType category.
    """
    @staticmethod
    def get_tester(form_type: str) -> Any:
        """
        Maps a classification label to its corresponding behavioral test runner class instance.
        """
        strategy_map = {
            "CONTACT": ContactFormTester,
            "NEWSLETTER": NewsletterFormTester,
            "LOGIN": LoginFormTester,
            "SEARCH": SearchFormTester,
            "BOOKING": UnknownFormTester,  # Fallback target configurations
            "QUOTE": UnknownFormTester,
            "UNKNOWN": UnknownFormTester
        }

        tester_class = strategy_map.get(form_type, UnknownFormTester)
        logger.info(f"StrategyFactory dispatched execution strategy: {tester_class.__name__} for type {form_type}")
        
        # Instantiate and return the dedicated test strategy class
        return tester_class()