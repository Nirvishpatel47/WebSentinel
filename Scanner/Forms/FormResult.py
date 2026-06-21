#!/usr/bin/env python3
from typing import List, Optional

class FormResult:
    """
    Responsibility: Standardized data model to store testing results from the specific strategies.
    """
    def __init__(
        self, 
        success: bool, 
        errors: List[str], 
        messages: List[str], 
        timings: float,
        screenshot_path: Optional[str] = None
    ):
        self.success: bool = success
        self.errors: List[str] = errors
        self.messages: List[str] = messages
        self.timings: float = timings
        self.screenshots: List[str] = [screenshot_path] if screenshot_path else []

    def to_dict(self) -> dict:
        """Converts the model state into a serializeable dictionary structure."""
        return {
            "success": self.success,
            "errors": self.errors,
            "messages": self.messages,
            "timings": f"{self.timings:.3f}s",
            "screenshots": self.screenshots
        }