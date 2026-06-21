#!/usr/bin/env python3

from dataclasses import dataclass, field
from typing import List


@dataclass
class FormResult:
    success: bool = False
    errors: List[str] = field(default_factory=list)
    messages: List[str] = field(default_factory=list)
    timings: float = 0.0

    before_screenshot: str | None = None
    after_screenshot: str | None = None
    failure_screenshot: str | None = None

    def to_dict(self):
        return {
            "success": self.success,
            "errors": self.errors,
            "messages": self.messages,
            "timings": round(self.timings,3),
            "before_screenshot": self.before_screenshot,
            "after_screenshot": self.after_screenshot,
            "failure_screenshot": self.failure_screenshot
        }