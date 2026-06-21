#!/usr/bin/env python3
from typing import List, Dict, Any

class FormClassifier:
    """
    Determines the specific FormType classification based on string markers, 
    input element footprints, and keywords.
    """
    def classify(self, action: str, method: str, fields: List[Dict[str, Any]]) -> str:
        """
        Analyzes form structures to return one of the explicit architecture states:
        CONTACT, NEWSLETTER, LOGIN, SEARCH, QUOTE, BOOKING, UNKNOWN
        """
        action_lower = action.lower()
        
        # Aggregate structural counts to detect field distribution patterns
        field_types = [f.get("type", "") for f in fields]
        field_names = [f.get("name", "").lower() for f in fields]
        field_ids = [f.get("id", "").lower() for f in fields]
        placeholders = [f.get("placeholder", "").lower() for f in fields]
        
        # Create a unified string list to look for keyword matches
        text_pool = field_names + field_ids + placeholders + [action_lower]

        # 1. SEARCH Classification Rule
        if any(x in text_pool for x in ["search", "q", "query", "term"]) or "search" in action_lower:
            if "password" not in field_types:
                return "SEARCH"

        # 2. LOGIN / AUTH Classification Rule
        if "password" in field_types or any(x in text_pool for x in ["login", "signin", "auth", "credential"]):
            return "LOGIN"

        # 3. NEWSLETTER Classification Rule
        if len(fields) <= 3 and any(x in text_pool for x in ["newsletter", "subscribe", "sub", "signup"]):
            if "email" in field_types or any("email" in n for n in field_names):
                return "NEWSLETTER"

        # 4. BOOKING / RESERVATION Classification Rule
        booking_keywords = ["booking", "reserve", "reservation", "date", "checkin", "checkout", "appointment"]
        if any(x in n for x in booking_keywords for n in text_pool) or "date" in field_types:
            return "BOOKING"

        # 5. QUOTE / PRICING Classification Rule
        quote_keywords = ["quote", "estimate", "pricing", "budget", "calculator", "company"]
        if any(x in n for x in quote_keywords for n in text_pool):
            return "QUOTE"

        # 6. CONTACT Classification Rule
        contact_keywords = ["contact", "support", "message", "feedback", "inquiry", "subject"]
        if any(x in n for x in contact_keywords for n in text_pool) or "textarea" in field_types:
            return "CONTACT"

        # Fallthrough State
        return "UNKNOWN"