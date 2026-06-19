"""
data_generator.py
Realistic test data generation for form fields.
Extends original TEST_DATA with more field types and dynamic values (e.g. dates).
"""

from datetime import datetime, date
from typing import Dict, Any, Optional
import os
import tempfile

# Base test data (from original script)
TEST_DATA = {
    "name": "John Doe",
    "email": "qa-test@example.com",
    "phone": "9876543210",
    "company": "QA Automation Ltd",
    "job_title": "QA Engineer",
    "message": "This is an automated QA test submission for form validation.",
    "password": "Password@123",
    "unknown": "Test Value"
}


def get_test_value(field_type: str, field_info: Optional[Dict[str, Any]] = None) -> Any:
    """
    Return appropriate test value for the classified field type.
    Supports all new categories from classifier.
    """
    field_type = (field_type or "unknown").lower()

    if field_type == "email":
        return TEST_DATA["email"]
    if field_type == "password":
        return TEST_DATA["password"]
    if field_type == "phone":
        return TEST_DATA["phone"]
    if field_type == "company":
        return TEST_DATA["company"]
    if field_type == "job_title":
        return TEST_DATA["job_title"]
    if field_type == "message":
        return TEST_DATA["message"]
    if field_type == "name":
        return TEST_DATA["name"]
    if field_type == "first_name":
        return "John"
    if field_type == "last_name":
        return "Doe"
    if field_type == "address":
        return "123 Automation Street, Suite 100"
    if field_type == "city":
        return "Testville"
    if field_type == "state":
        return "California"
    if field_type == "country":
        return "United States"
    if field_type == "zipcode":
        return "90210"
    if field_type == "date":
        # Use today's date in YYYY-MM-DD format (common for date inputs)
        return date.today().isoformat()
    if field_type == "number":
        return "42"
    if field_type == "checkbox":
        # For checkboxes we usually just check them (no value needed, or "on")
        return True
    if field_type == "radio":
        # Value will be handled by group selection in filler
        return True
    if field_type == "select":
        # Filler will pick first valid option; return None here
        return None
    if field_type == "unknown":
        # Try to infer from placeholder or name if possible
        if field_info:
            placeholder = (field_info.get("placeholder") or "").lower()
            if "search" in placeholder:
                return "test query"
            if "url" in placeholder or "website" in placeholder:
                return "https://example.com"
        return TEST_DATA["unknown"]

    return TEST_DATA.get(field_type, TEST_DATA["unknown"])


def get_dummy_file_path() -> Optional[str]:
    """
    Create a temporary dummy file for file input testing.
    Returns path or None if creation fails.
    """
    try:
        fd, path = tempfile.mkstemp(suffix=".txt", prefix="qa_test_file_")
        with os.fdopen(fd, "w") as f:
            f.write("This is a test file for QA form automation.\n")
            f.write("Generated automatically for file upload field testing.\n")
        return path
    except Exception:
        return None


def should_fill_field(field_info: Dict[str, Any]) -> bool:
    """
    Decide if we should attempt to fill this field.
    Skip hidden, disabled, readonly unless explicitly required.
    """
    if not field_info:
        return False

    # Skip hidden inputs (except if it's a honeypot we want to avoid, but usually skip)
    if field_info.get("type") == "hidden":
        return False

    # Skip disabled
    # Note: Playwright locator for disabled is tricky; we check attribute
    # In filler we will also check via evaluate if needed
    if field_info.get("disabled") or field_info.get("readonly"):
        # Only fill if required (rare for disabled)
        if not field_info.get("required"):
            return False

    return True