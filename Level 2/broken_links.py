#!/usr/bin/env python3
"""
Production-Grade Broken Resource Scanner v2
- Crawls multi-page websites
- Actively reveals dropdown menus, accordions, and hidden content
- Uses smart selectors + heuristic interaction
- Production ready for real websites
"""

import asyncio
import httpx
import json
from urllib.parse import urljoin, urlparse, urldefrag
from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeout
from typing import Dict, List, Set, Tuple, Optional
from typing import Dict, List, Set, Tuple



# =========================
# CONFIG
# =========================
CONCURRENCY = 20
TIMEOUT = 12
MAX_PAGES = 50
MAX_DROPDOWNS_TO_INTERACT = 15
DROPDOWN_INTERACTION_TIMEOUT = 800  
MAX_INTERACTIONS = 25
WAIT_AFTER_ACTION_MS = 400


# =========================
# URL HELPERS
# =========================
def normalize(base: str, url: str) -> Optional[str]:
    if not url or url.startswith(("javascript:", "mailto:", "tel:", "data:")):
        return None
    try:
        full_url = urljoin(base, url)
        full_url, _ = urldefrag(full_url)
        return full_url.strip()
    except Exception:
        return None


def get_domain(url: str) -> Optional[str]:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return None


def is_internal(base_domain: str, url: str) -> bool:
    return get_domain(url) == base_domain or url.startswith(("/", "#"))

# -----------------------------
# STABLE PAGE SIGNATURE
# -----------------------------
async def get_page_signature(page: Page) -> str:
    """
    Lightweight fingerprint to detect DOM changes.
    """
    try:
        return await page.evaluate("""
            () => document.body.innerText.length + '|' +
                  document.querySelectorAll('*').length
        """)
    except:
        return ""


# -----------------------------
# SAFE ELEMENT IDENTIFICATION
# -----------------------------
async def get_element_key(element) -> str:
    """
    Stable identity instead of bounding-box dedupe.
    """
    try:
        return await element.evaluate("""
            el => el.outerHTML.slice(0, 200)
        """)
    except:
        return ""


# -----------------------------
# MAIN FUNCTION (REWRITTEN)
# -----------------------------
async def reveal_dropdowns_and_extract(page: Page) -> Dict[str, List[str]]:
    """
    Production-grade UI interaction engine:
    - Extracts resources
    - Expands dropdowns / menus / accordions / tabs
    - Uses state validation (not blind clicking)
    - Prevents duplicate or unsafe interactions
    """

    all_resources: Dict[str, List[str]] = {
        "links": [],
        "images": [],
        "scripts": [],
        "styles": [],
        "videos": [],
        "audios": [],
        "iframes": [],
    }

    seen_elements: Set[str] = set()
    interactions = 0

    # -----------------------------
    # BASE EXTRACTION
    # -----------------------------
    try:
        initial = await extract_visible_resources(page)
        merge_resources(all_resources, initial)
    except:
        pass

    # -----------------------------
    # COLLECT INTERACTIVE ELEMENTS
    # -----------------------------
    try:
        candidates = await page.locator("""
            [aria-haspopup],
            [aria-expanded],
            [aria-controls],
            button,
            a,
            [role='button']
        """).all()
    except:
        candidates = []

    # -----------------------------
    # FILTER + DEDUPE
    # -----------------------------
    valid_triggers = []

    for el in candidates:
        try:
            if not await el.is_visible():
                continue

            key = await get_element_key(el)

            if not key or key in seen_elements:
                continue

            seen_elements.add(key)
            valid_triggers.append(el)

        except:
            continue

    valid_triggers = valid_triggers[:MAX_INTERACTIONS]

    # -----------------------------
    # MAIN INTERACTION LOOP
    # -----------------------------
    for trigger in valid_triggers:

        if interactions >= MAX_INTERACTIONS:
            break

        try:
            before_state = await get_page_signature(page)

            # -------------------------
            # STRATEGY 1: HOVER EXPANSION
            # -------------------------
            try:
                await trigger.hover(timeout=800)
                await page.wait_for_timeout(WAIT_AFTER_ACTION_MS)
            except PlaywrightTimeout:
                pass

            after_hover = await get_page_signature(page)

            if after_hover != before_state:
                try:
                    updated = await extract_visible_resources(page)
                    merge_resources(all_resources, updated)
                except:
                    pass

            # -------------------------
            # STRATEGY 2: CLICK EXPANSION
            # -------------------------
            clicked = False

            try:
                aria = await trigger.get_attribute("aria-expanded")
                cls = await trigger.get_attribute("class") or ""

                # Only click if it looks interactive
                if aria is not None or "menu" in cls or "dropdown" in cls:
                    await trigger.click(timeout=800, force=True)
                    clicked = True
            except:
                pass

            if clicked:
                await page.wait_for_timeout(WAIT_AFTER_ACTION_MS)

                after_click = await get_page_signature(page)

                if after_click != before_state:
                    try:
                        updated = await extract_visible_resources(page)
                        merge_resources(all_resources, updated)
                    except:
                        pass

                # close menu safely
                try:
                    await page.keyboard.press("Escape")
                except:
                    pass

            interactions += 1

        except:
            continue

    # -----------------------------
    # FINAL EXTRACTION PASS
    # -----------------------------
    try:
        final = await extract_visible_resources(page)
        merge_resources(all_resources, final)
    except:
        pass

    return all_resources


def merge_resources(target: Dict, source: Dict):
    """Merge two resource dictionaries without duplicates"""
    for key in target:
        if key in source:
            target[key] = list(set(target[key] + source[key]))


async def extract_visible_resources(page) -> Dict[str, List[str]]:
    """Extract all resources currently visible in DOM"""
    return await page.evaluate("""
        () => {
            const getAttr = (els, attr) => Array.from(els).map(e => e.getAttribute(attr)).filter(Boolean);
            
            return {
                links: getAttr(document.querySelectorAll('a[href]'), 'href'),
                images: getAttr(document.querySelectorAll('img[src]'), 'src'),
                scripts: getAttr(document.querySelectorAll('script[src]'), 'src'),
                styles: getAttr(document.querySelectorAll('link[rel="stylesheet"]'), 'href'),
                videos: getAttr(document.querySelectorAll('video[src]'), 'src'),
                video_sources: getAttr(document.querySelectorAll('video source[src]'), 'src'),
                audios: getAttr(document.querySelectorAll('audio[src]'), 'src'),
                audio_sources: getAttr(document.querySelectorAll('audio source[src]'), 'src'),
                iframes: getAttr(document.querySelectorAll('iframe[src]'), 'src'),
                video_posters: getAttr(document.querySelectorAll('video[poster]'), 'poster')
            };
        }
    """)


# =========================
# HTTP CHECKER + WORKER (same as before)
# =========================
async def check_url(client: httpx.AsyncClient, url: str) -> Tuple[str, str, Optional[int]]:
    try:
        response = await client.get(url, timeout=TIMEOUT, follow_redirects=True)
        status = response.status_code
        if 200 <= status < 300:
            return url, "OK", status
        elif 300 <= status < 400:
            return url, "REDIRECT", status
        else:
            return url, "BROKEN", status
    except httpx.TimeoutException:
        return url, "TIMEOUT", None
    except Exception:
        return url, "ERROR", None


async def worker(queue: asyncio.Queue, client: httpx.AsyncClient, results: List):
    while True:
        url = await queue.get()
        if url is None:
            break
        result = await check_url(client, url)
        results.append(result)
        queue.task_done()


# =========================
# MAIN SCANNER
# =========================
async def scan_site(start_url: str) -> Dict:
    print(f"🚀 Starting Production-Grade Scan: {start_url}\n")

    base_domain = get_domain(start_url)
    visited_pages: Set[str] = set()
    page_queue: asyncio.Queue = asyncio.Queue()
    resource_set: Set[str] = set()

    await page_queue.put(start_url)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )

        print("📄 Crawling pages + revealing hidden content...\n")

        while not page_queue.empty() and len(visited_pages) < MAX_PAGES:
            current_url = await page_queue.get()
            if current_url in visited_pages:
                page_queue.task_done()
                continue

            visited_pages.add(current_url)
            print(f"→ Visiting: {current_url}")

            try:
                page = await context.new_page()
                await page.goto(current_url, timeout=50000, wait_until="domcontentloaded")
                await page.wait_for_load_state("networkidle", timeout=10000)

                # === KEY IMPROVEMENT: Reveal dropdowns before extracting ===
                resources = await reveal_dropdowns_and_extract(page)

                # Collect resources
                for key in resources:
                    for raw_url in resources[key]:
                        norm = normalize(current_url, raw_url)
                        if norm:
                            resource_set.add(norm)

                # Discover new internal pages
                for link in resources.get("links", []):
                    norm_link = normalize(current_url, link)
                    if norm_link and is_internal(base_domain, norm_link):
                        if norm_link not in visited_pages:
                            await page_queue.put(norm_link)

                await page.close()

            except Exception as e:
                print(f"   ⚠️ Error on {current_url}: {str(e)[:80]}")
            finally:
                page_queue.task_done()

        await browser.close()

    print(f"\n✅ Crawled {len(visited_pages)} pages")
    print(f"📦 Found {len(resource_set)} unique resources\n")

    # Check resources
    print("🔍 Checking all resources for broken items...\n")
    async with httpx.AsyncClient(follow_redirects=True, timeout=TIMEOUT) as client:
        queue: asyncio.Queue = asyncio.Queue()
        results: List[Tuple] = []

        for url in resource_set:
            await queue.put(url)

        workers = [asyncio.create_task(worker(queue, client, results)) for _ in range(CONCURRENCY)]
        await queue.join()
        for _ in workers:
            await queue.put(None)
        await asyncio.gather(*workers, return_exceptions=True)

        all_results = results

    # Analysis
    ok = [r for r in all_results if r[1] == "OK"]
    broken = [r for r in all_results if r[1] == "BROKEN"]
    redirects = [r for r in all_results if r[1] == "REDIRECT"]
    errors = [r for r in all_results if r[1] in ["ERROR", "TIMEOUT"]]

    broken_images = [b for b in broken if any(ext in b[0].lower() for ext in ['.jpg','.png','.gif','.webp','.svg','.ico'])]
    broken_links = [b for b in broken if b not in broken_images]

    # Report
    print("=" * 70)
    print("📊 PRODUCTION-GRADE BROKEN RESOURCE REPORT")
    print("=" * 70)
    print(f"Pages crawled:          {len(visited_pages)}")
    print(f"Total resources found:  {len(all_results)}")
    print(f"✅ OK:                  {len(ok)}")
    print(f"🔀 Redirects:           {len(redirects)}")
    print(f"❌ BROKEN:              {len(broken)}")
    print(f"⚠️  Errors/Timeouts:    {len(errors)}")
    print("-" * 70)

    if broken:
        print(f"\n❌ BROKEN RESOURCES ({len(broken)}):")
        for url, status, code in broken:
            print(f"   [{code or status}] {url}")

    if errors:
        print(f"\n⚠️  ERRORS / TIMEOUTS ({len(errors)}):")
        for url, status, code in errors:
            print(f"   [{status}] {url}")

    print("\n" + "=" * 70)

    response = {
        "success": True,
        "start_url": start_url,
        "pages_crawled": len(visited_pages),
        "visited_pages": sorted(list(visited_pages)),
        "summary": {
            "total_resources": len(all_results),
            "ok": len(ok),
            "redirects": len(redirects),
            "broken": len(broken),
            "errors_timeouts": len(errors),
            "broken_images": len(broken_images),
            "broken_links": len(broken_links)
        },
        "broken_resources": [
            {"url": url, "status": status, "http_code": code}
            for url, status, code in broken
        ],
        "error_resources": [
            {"url": url, "status": status, "http_code": code}
            for url, status, code in errors
        ]
    }

    return response


# =========================
# RUN
# =========================
if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5500/ETHOWT/TESTING/Website-5/portfolio.html"

    result = asyncio.run(scan_site(target))

    print("\n📦 FINAL JSON RESPONSE:\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))