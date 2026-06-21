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
        
        field_types = [f.get("type", "") for f in fields]
        field_names = [f.get("name", "").lower() for f in fields]
        field_ids = [f.get("id", "").lower() for f in fields]
        placeholders = [f.get("placeholder", "").lower() for f in fields]

        if ("textarea" in field_types and any("email" in x for x in field_names)):
            return "CONTACT"
        
        labels = [f.get("label", "").lower() for f in fields]

        text_blob = " ".join(field_names + field_ids + placeholders + labels + [action_lower])

        if any(x in text_blob for x in ["search", "query", "term"]) or "search" in action_lower:
            if "password" not in field_types:
                return "SEARCH"

        if "password" in field_types or any(x in text_blob for x in ["login", "signin", "auth", "credential"]):
            return "LOGIN"

        if len(fields) <= 3 and any(x in text_blob for x in ["newsletter", "subscribe", "sub", "signup"]):
            if "email" in field_types or any("email" in n for n in field_names):
                return "NEWSLETTER"

        booking_keywords = ["booking", "reserve", "reservation", "date", "checkin", "checkout", "appointment"]
        if any(x in n for x in booking_keywords for n in text_blob) or "date" in field_types:
            return "BOOKING"

        quote_keywords = ["quote", "estimate", "pricing", "budget", "calculator", "company"]
        if any(x in n for x in quote_keywords for n in text_blob):
            return "QUOTE"

        contact_keywords = ["contact", "support", "message", "feedback", "inquiry", "subject"]
        if any(x in n for x in contact_keywords for n in text_blob) or "textarea" in field_types:
            return "CONTACT"

        return "UNKNOWN"