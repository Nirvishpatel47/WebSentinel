"""
reporter.py
Result collection, JSON reporting, and screenshot capture (only after submission).
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from playwright.async_api import Page


def get_domain(url: str) -> str:
    """Extract clean domain for folder naming."""
    try:
        netloc = urlparse(url).netloc
        return netloc.replace("www.", "").replace(":", "_")
    except Exception:
        return "unknown_site"


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


async def capture_screenshot_after_submit(
    page: Page,
    site_url: str,
    form_index: int,
    output_dir: str = "screenshots"
) -> Optional[str]:
    """
    Capture ONE screenshot AFTER submission.
    Saves to screenshots/<domain>/form_<index>_<timestamp>.png
    Returns relative path or None on failure.
    """
    try:
        domain = get_domain(site_url)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"form_{form_index}_{timestamp}.png"
        dir_path = os.path.join(output_dir, domain)
        ensure_dir(dir_path)
        full_path = os.path.join(dir_path, filename)

        await page.screenshot(path=full_path, full_page=True)
        return full_path
    except Exception as e:
        print(f"[reporter] Screenshot failed: {str(e)[:80]}")
        return None


def create_result_entry(
    page_url: str,
    form_index: int,
    field_count: int,
    submitted: bool,
    success: bool,
    confidence: float,
    screenshot_path: Optional[str] = None,
    reason: str = "",
    error: Optional[str] = None
) -> Dict[str, Any]:
    """Standardized result dict for the final report."""
    return {
        "page_url": page_url,
        "form_index": form_index,
        "field_count": field_count,
        "submitted": submitted,
        "success": success,
        "confidence": round(confidence, 2),
        "screenshot": screenshot_path,
        "reason": reason,
        "error": error,
        "timestamp": datetime.now().isoformat()
    }


def generate_report(
    site: str,
    pages_scanned: int,
    forms_found: int,
    forms_tested: int,
    results: List[Dict[str, Any]],
    output_path: str = "reports/qa_form_report.json"
) -> str:
    """
    Write final JSON report.
    Returns the path to the saved report.
    """
    report = {
        "site": site,
        "scan_timestamp": datetime.now().isoformat(),
        "pages_scanned": pages_scanned,
        "forms_found": forms_found,
        "forms_tested": forms_tested,
        "summary": {
            "successful": sum(1 for r in results if r.get("success")),
            "failed": sum(1 for r in results if not r.get("success") and r.get("submitted")),
            "not_submitted": sum(1 for r in results if not r.get("submitted"))
        },
        "results": results
    }

    ensure_dir(os.path.dirname(output_path) or ".")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    return output_path


def print_summary(report_path: str) -> None:
    """Pretty print a short summary to console."""
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print("\n" + "=" * 60)
        print("QA FORM AUTOMATION REPORT SUMMARY")
        print("=" * 60)
        print(f"Site: {data.get('site')}")
        print(f"Pages scanned: {data.get('pages_scanned')}")
        print(f"Forms found:   {data.get('forms_found')}")
        print(f"Forms tested:  {data.get('forms_tested')}")
        summary = data.get("summary", {})
        print(f"Successful:    {summary.get('successful', 0)}")
        print(f"Failed:        {summary.get('failed', 0)}")
        print(f"Not submitted: {summary.get('not_submitted', 0)}")
        print(f"\nFull report saved to: {report_path}")
        print("=" * 60 + "\n")
    except Exception as e:
        print(f"[reporter] Could not print summary: {e}")