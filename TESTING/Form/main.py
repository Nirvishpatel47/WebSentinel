"""
main.py
Entry point and orchestrator for the Website-wide Form QA Automation Engine.

Usage:
    python main.py https://example.com [--max-pages 30] [--max-depth 2] [--headless]

Extends the original single-page process_page into full site crawling + testing.
All original functions/logic preserved where possible via imports.
"""

import argparse
import asyncio
import os
from urllib.parse import urlparse
from typing import List, Dict, Any

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

# Import all modules
from crawler import crawl_site
from scanner import scan_page_for_forms
from classifier import classify_field  # already used inside scanner
from filler import fill_field
from submitter import find_submit_button, submit_form, wait_after_submit
from detector import detect_result
from reporter import (
    capture_screenshot_after_submit,
    create_result_entry,
    generate_report,
    print_summary,
    get_domain
)


async def process_form(
    page: Page,
    form_data: Dict[str, Any],
    page_url: str,
    form_index: int
) -> Dict[str, Any]:
    """
    Process a single form: fill fields -> find & click submit -> detect result -> screenshot.
    Returns a result dict for the report.
    """
    form_locator = form_data.get("locator")
    fields = form_data.get("fields", [])
    field_count = form_data.get("field_count", 0)

    print(f"\n  [Form #{form_index}] Fields found: {field_count}")

    submitted = False
    success = False
    confidence = 0.0
    reason = ""
    screenshot_path = None
    error_msg = None

    try:
        # === FILL PHASE ===
        for f_idx, field_info in enumerate(fields):
            classified = field_info.get("classified_type", "unknown")
            print(f"    Field #{f_idx}: {classified} ({field_info.get('tag')})")

            # Get fresh locator for this field (important after previous fills)
            # Re-locate by trying multiple strategies
            locator = None
            try:
                if field_info.get("id"):
                    locator = page.locator(f"#{field_info['id']}")
                elif field_info.get("name"):
                    locator = page.locator(f"[name='{field_info['name']}']")
                else:
                    # Fallback: use original form's nth field
                    if form_locator:
                        locator = form_locator.locator("input, textarea, select").nth(f_idx)
                    else:
                        locator = page.locator("input, textarea, select").nth(f_idx)
            except Exception:
                pass

            if locator:
                try:
                    await fill_field(locator, classified, field_info)
                except Exception as fill_err:
                    print(f"      Fill warning: {str(fill_err)[:60]}")

        # === SUBMIT PHASE ===
        submit_btn = None
        if form_locator:
            submit_btn = await find_submit_button(form_locator)
        if not submit_btn:
            # Try page-wide search as fallback
            submit_btn = await find_submit_button(page.locator("body"))

        if not submit_btn:
            print("    No submit button found. Skipping submission.")
            return create_result_entry(
                page_url, form_index, field_count,
                submitted=False, success=False, confidence=0.0,
                reason="no submit button found"
            )

        print("    Submit button found. Submitting...")

        old_url = page.url

        # Click submit
        submit_ok = await submit_form(form_locator or page.locator("form").first, submit_btn)
        if not submit_ok:
            error_msg = "submit click failed"
        else:
            submitted = True
            await wait_after_submit(page, 2500)

            # === DETECT PHASE ===
            result = await detect_result(page, old_url, form_locator)
            success = result.get("success", False)
            confidence = result.get("confidence", 0.0)
            reason = result.get("reason", "")

            print(f"    RESULT: success={success}, confidence={confidence:.2f}, reason={reason[:60]}")

            # === SCREENSHOT (ONLY AFTER SUBMIT) ===
            if submitted:
                screenshot_path = await capture_screenshot_after_submit(
                    page, page_url, form_index
                )
                if screenshot_path:
                    print(f"    Screenshot saved: {screenshot_path}")

    except Exception as e:
        error_msg = str(e)[:150]
        print(f"    ERROR processing form: {error_msg}")

    return create_result_entry(
        page_url=page_url,
        form_index=form_index,
        field_count=field_count,
        submitted=submitted,
        success=success,
        confidence=confidence,
        screenshot_path=screenshot_path,
        reason=reason,
        error=error_msg
    )


async def process_page(page: Page, url: str) -> List[Dict[str, Any]]:
    """
    Process one page: scan forms -> process each form.
    Returns list of result entries for this page.
    """
    print(f"\n{'='*60}")
    print(f"Processing: {url}")
    print(f"{'='*60}")

    page_results = []

    try:
        await page.goto(url, wait_until="networkidle", timeout=20000)
        await page.wait_for_timeout(1200)  # settle

        forms_data = await scan_page_for_forms(page)
        print(f"Forms / field groups found: {len(forms_data)}")

        for form_data in forms_data:
            form_idx = form_data["form_index"]
            res = await process_form(page, form_data, url, form_idx)
            page_results.append(res)

    except Exception as e:
        print(f"Page processing error: {str(e)[:120]}")
        page_results.append(create_result_entry(
            url, -1, 0, submitted=False, success=False, confidence=0.0,
            reason="page load/scan failed", error=str(e)[:120]
        ))

    return page_results


async def run_qa_engine(
    root_url: str,
    max_pages: int = 30,
    max_depth: int = 2,
    headless: bool = True,
    report_path: str = "reports/qa_form_report.json"
) -> str:
    """
    Main async entry point.
    Crawls site, tests all discovered forms, generates report + screenshots.
    """
    print(f"\n🚀 Starting QA Form Automation Engine")
    print(f"   Root URL   : {root_url}")
    print(f"   Max pages  : {max_pages}")
    print(f"   Max depth  : {max_depth}")
    print(f"   Headless   : {headless}\n")

    all_results: List[Dict[str, Any]] = []
    pages_scanned = 0
    total_forms_found = 0
    total_forms_tested = 0

    async with async_playwright() as p:
        browser: Browser = await p.chromium.launch(headless=headless)
        context: BrowserContext = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            ignore_https_errors=True
        )

        # === PHASE 1: CRAWL ===
        print("🔍 Starting website crawl...")
        urls_to_test = await crawl_site(context, root_url, max_pages, max_depth)
        print(f"   Discovered {len(urls_to_test)} pages to test.\n")

        # Use a single page for testing (goto between URLs)
        test_page: Page = await context.new_page()

        for idx, url in enumerate(urls_to_test):
            pages_scanned += 1
            page_results = await process_page(test_page, url)

            for r in page_results:
                all_results.append(r)
                if r.get("field_count", 0) > 0:
                    total_forms_found += 1
                if r.get("submitted"):
                    total_forms_tested += 1

        await test_page.close()
        await context.close()
        await browser.close()

    # === FINAL REPORT ===
    domain = get_domain(root_url)
    final_report_path = report_path.replace("qa_form_report.json", f"qa_form_report_{domain}.json")

    report_file = generate_report(
        site=root_url,
        pages_scanned=pages_scanned,
        forms_found=total_forms_found,
        forms_tested=total_forms_tested,
        results=all_results,
        output_path=final_report_path
    )

    print_summary(report_file)
    return report_file


def parse_args():
    parser = argparse.ArgumentParser(description="Website-wide Form QA Automation Engine")
    parser.add_argument("url", help="Root URL to crawl and test (e.g. https://example.com)")
    parser.add_argument("--max-pages", type=int, default=30, help="Maximum pages to crawl (default: 30)")
    parser.add_argument("--max-depth", type=int, default=2, help="Maximum crawl depth (default: 2)")
    parser.add_argument("--headless", action="store_true", default=True, help="Run browser in headless mode")
    parser.add_argument("--no-headless", dest="headless", action="store_false", help="Show browser window")
    parser.add_argument("--report", default="reports/qa_form_report.json", help="Output JSON report path")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Ensure report/screenshot dirs exist
    os.makedirs("reports", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)

    try:
        report_path = asyncio.run(
            run_qa_engine(
                root_url=args.url,
                max_pages=args.max_pages,
                max_depth=args.max_depth,
                headless=args.headless,
                report_path=args.report
            )
        )
        print(f"\n✅ Done. Report: {report_path}")
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()