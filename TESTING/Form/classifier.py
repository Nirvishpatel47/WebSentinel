"""
classifier.py
Improved field classification for QA form automation.
Extends the original classify_field logic with more categories and better matching.
Preserves compatibility with existing field info structure.
"""

from typing import Dict, Optional, Any

# Supported field classifications
SUPPORTED_TYPES = [
    "name", "first_name", "last_name",
    "email", "phone", "company", "job_title",
    "address", "city", "state", "country", "zipcode",
    "message", "password", "date", "number",
    "checkbox", "radio", "select", "unknown"
]


def classify_field(field_info: Dict[str, Any]) -> str:
    """
    Classify a form field based on its metadata.
    Uses name, id, placeholder, label, aria_label, type, and tag.
    Priority: explicit type attributes first, then keyword matching (specific -> general).
    """
    if not field_info:
        return "unknown"

    # Combine all text signals into one lowercase string
    text_parts = []
    for key in ["name", "id", "placeholder", "label", "aria_label", "type"]:
        val = field_info.get(key)
        if val:
            text_parts.append(str(val).lower())

    text = " ".join(text_parts)
    tag = (field_info.get("tag") or "").lower()
    ftype = (field_info.get("type") or "").lower()

    # === Priority 1: Explicit input types ===
    if ftype == "email":
        return "email"
    if ftype == "password":
        return "password"
    if ftype == "tel":
        return "phone"
    if ftype in ["date", "datetime-local"]:
        return "date"
    if ftype == "number":
        return "number"
    if ftype == "checkbox":
        return "checkbox"
    if ftype == "radio":
        return "radio"
    if tag == "select":
        return "select"

    # === Priority 2: Strong keyword matches (order matters - specific first) ===
    # Email / Phone / Password already handled above, but double-check keywords
    if any(x in text for x in ["email", "e-mail", "mail"]):
        return "email"
    if any(x in text for x in ["password", "passwd", "pwd"]):
        return "password"
    if any(x in text for x in ["phone", "mobile", "tel", "contact", "cell"]):
        return "phone"

    # Name variants (check specific before generic "name")
    if any(x in text for x in ["first_name", "firstname", "first name", "fname"]):
        return "first_name"
    if any(x in text for x in ["last_name", "lastname", "last name", "lname", "surname"]):
        return "last_name"
    if any(x in text for x in ["full_name", "fullname", "your name", "full name"]):
        return "name"

    # Company / Organization
    if any(x in text for x in ["company", "organization", "org", "business", "employer"]):
        return "company"

    # Job / Role
    if any(x in text for x in ["job_title", "jobtitle", "title", "role", "designation", "position", "occupation"]):
        return "job_title"

    # Address fields
    if any(x in text for x in ["address", "street", "addr"]):
        return "address"
    if any(x in text for x in ["city", "town", "locality"]):
        return "city"
    if any(x in text for x in ["state", "province", "region"]):
        return "state"
    if any(x in text for x in ["country", "nation"]):
        return "country"
    if any(x in text for x in ["zip", "zipcode", "postal", "pincode", "postcode"]):
        return "zipcode"

    # Message / Comment
    if any(x in text for x in ["message", "comment", "description", "feedback", "query", "enquiry", "note"]):
        return "message"

    # Generic name (last resort for name-like fields)
    if "name" in text and "first" not in text and "last" not in text:
        return "name"

    # Number (if not already caught)
    if "number" in text or "qty" in text or "quantity" in text or "amount" in text:
        return "number"

    # Date fallback
    if any(x in text for x in ["date", "dob", "birthday", "birth"]):
        return "date"

    return "unknown"


def get_field_display_name(field_type: str) -> str:
    """Human readable name for logging/reporting."""
    mapping = {
        "first_name": "First Name",
        "last_name": "Last Name",
        "name": "Full Name",
        "email": "Email Address",
        "phone": "Phone Number",
        "company": "Company",
        "job_title": "Job Title",
        "address": "Address",
        "city": "City",
        "state": "State/Province",
        "country": "Country",
        "zipcode": "ZIP/Postal Code",
        "message": "Message/Comment",
        "password": "Password",
        "date": "Date",
        "number": "Number",
        "checkbox": "Checkbox",
        "radio": "Radio Button",
        "select": "Dropdown",
        "unknown": "Unknown Field"
    }
    return mapping.get(field_type, field_type.title())


# For backward compatibility with original script
def classify_field_legacy(field: Dict[str, Any]) -> str:
    """Original logic preserved for compatibility."""
    text = " ".join(
        str(x).lower()
        for x in [
            field.get("name"),
            field.get("id"),
            field.get("placeholder"),
            field.get("label"),
            field.get("aria_label"),
            field.get("type")
        ]
        if x
    )

    if "email" in text:
        return "email"
    if "password" in text:
        return "password"
    if any(x in text for x in ["phone", "mobile", "contact"]):
        return "phone"
    if "company" in text:
        return "company"
    if any(x in text for x in ["role", "designation", "title"]):
        return "job_title"
    if any(x in text for x in ["message", "comment", "description"]):
        return "message"
    if "name" in text:
        return "name"
    return "unknown"