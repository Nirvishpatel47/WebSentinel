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
import logging
import os
import re


logging.basicConfig(
    filename="scan.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

screenshots_dir = r"F:\Smart AI workflow\ETHOWT\proofs"

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

NON_HTML = (
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".svg",
    ".webp",
    ".mp4",
    ".mp3",
    ".css",
    ".js",
    ".zip"
)

def should_check_url(url: str) -> bool:

    if not url:
        return False

    scheme = urlparse(url).scheme.lower()

    SKIP_SCHEMES = {
        "blob",
        "data",
        "javascript",
        "mailto",
        "tel",
        "sms",
        "whatsapp"
    }

    if scheme in SKIP_SCHEMES:
        return False

    return True

def is_html_page(url: str) -> bool:

    path = urlparse(url).path.lower()

    return not path.endswith(
        NON_HTML
    )

def safe_filename(text: str) -> str:
    return re.sub(
        r'[<>:"/\\\\|?*]',
        '_',
        text
    )

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
async def get_page_signature(page):
    return await page.evaluate("""
        () => {
            return JSON.stringify({
                text: document.body.innerText.length,
                elements: document.querySelectorAll('*').length,
                links: document.querySelectorAll('a').length,
                images: document.querySelectorAll('img').length
            });
        }
    """)


# -----------------------------
# SAFE ELEMENT IDENTIFICATION
# -----------------------------
async def get_element_key(element):
    try:
        return await element.evaluate("""
        el => JSON.stringify({
            tag: el.tagName,
            id: el.id,
            name: el.getAttribute('name'),
            text: el.innerText?.trim().slice(0,50)
        })
        """)
    except:
        return ""


# -----------------------------
# MAIN FUNCTION (REWRITTEN)
# -----------------------------
async def reveal_dropdowns_and_extract(page: Page) -> Dict[str, List[str]]:
    """
    Reveal menus/accordions/tabs and collect newly exposed resources.
    Safer and simpler than DOM-signature based approach.
    """

    all_resources = {
        "links": [],
        "images": [],
        "scripts": [],
        "styles": [],
        "videos": [],
        "audios": [],
        "iframes": [],
        "network": []
    }

    # --------------------------------
    # TRACK NETWORK REQUESTS
    # --------------------------------
    network_urls = set()

    def capture_response(response):
        try:
            network_urls.add(response.url)
        except:
            pass

    page.on("response", capture_response)

    # --------------------------------
    # INITIAL EXTRACTION
    # --------------------------------
    try:
        initial = await extract_visible_resources(page)
        merge_resources(all_resources, initial)
    except:
        pass

    # --------------------------------
    # FIND REAL INTERACTIVE CONTROLS
    # --------------------------------
    try:
        candidates = await page.locator("""
            button,
            [role='button'],
            [aria-expanded],
            [aria-haspopup],
            [aria-controls]
        """).all()
    except:
        candidates = []

    seen = set()
    interactions = 0

    # --------------------------------
    # PROCESS CONTROLS
    # --------------------------------
    for element in candidates:

        if interactions >= MAX_INTERACTIONS:
            break

        try:

            if not await element.is_visible():
                continue

            key = await get_element_key(element)

            if not key or key in seen:
                continue

            seen.add(key)

            before_count = sum(
                len(v)
                for k, v in all_resources.items()
                if k != "network"
            )

            # ------------------------
            # HOVER
            # ------------------------
            try:
                await element.hover(timeout=1000)
                await page.wait_for_timeout(500)
            except:
                pass

            # ------------------------
            # CLICK ONLY IF IT LOOKS
            # LIKE A TOGGLE
            # ------------------------
            try:

                aria = await element.get_attribute("aria-expanded")

                role = await element.get_attribute("role") or ""

                cls = (
                    await element.get_attribute("class")
                    or ""
                ).lower()

                looks_like_toggle = (
                    aria is not None
                    or "menu" in cls
                    or "dropdown" in cls
                    or "accordion" in cls
                    or role == "button"
                )

                if looks_like_toggle:

                    await element.click(
                        timeout=1000
                    )

                    await page.wait_for_timeout(500)

            except:
                pass

            # ------------------------
            # EXTRACT AGAIN
            # ------------------------
            try:

                updated = await extract_visible_resources(page)

                merge_resources(
                    all_resources,
                    updated
                )

            except:
                pass

            after_count = sum(
                len(v)
                for k, v in all_resources.items()
                if k != "network"
            )

            # Close dropdown safely
            try:
                await page.keyboard.press(
                    "Escape"
                )
            except:
                pass

            interactions += 1

            # If nothing new discovered,
            # move on quickly
            if after_count == before_count:
                continue

        except:
            continue

    # --------------------------------
    # FINAL EXTRACTION
    # --------------------------------
    try:

        final = await extract_visible_resources(page)

        merge_resources(
            all_resources,
            final
        )

    except:
        pass

    # --------------------------------
    # NETWORK RESOURCES
    # --------------------------------
    all_resources["network"] = list(
        network_urls
    )

    return all_resources


def merge_resources(target: Dict, source: Dict):
    """Merge two resource dictionaries without duplicates"""
    for key in target:
        if key in source:
            target[key] = list(set(target[key] + source[key]))


async def extract_visible_resources(page) -> Dict[str, List[str]]:
    """
    Extract resources currently present in the DOM.
    Returns raw URLs/paths exactly as found.
    """

    resources = await page.evaluate("""
    () => {

        const getAttr = (selector, attr) => {
            return [...document.querySelectorAll(selector)]
                .map(el => el.getAttribute(attr))
                .filter(Boolean);
        };

        return {

            links: getAttr(
                'a[href]',
                'href'
            ),

            images: [
                ...getAttr('img[src]', 'src'),
                ...getAttr('img[data-src]', 'data-src'),
                ...getAttr('img[data-lazy-src]', 'data-lazy-src')
            ],

            scripts: getAttr(
                'script[src]',
                'src'
            ),

            styles: getAttr(
                'link[rel="stylesheet"]',
                'href'
            ),

            videos: [
                ...getAttr('video[src]', 'src'),
                ...getAttr('video source[src]', 'src')
            ],

            audios: [
                ...getAttr('audio[src]', 'src'),
                ...getAttr('audio source[src]', 'src')
            ],

            iframes: getAttr(
                'iframe[src]',
                'src'
            ),

            posters: getAttr(
                'video[poster]',
                'poster'
            ),

            pictures: getAttr(
                'picture source[srcset]',
                'srcset'
            )
        };
    }
    """)
    for category, urls in resources.items():

        resources[category] = [
            url
            for url in urls
            if should_check_url(url)
        ]

    return resources


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
        elif status in {401, 403}:
            return url, "RESTRICTED", status
        elif status == 429:
            return url, "RATE_LIMITED", status
        elif 400 <= status < 500:
            return url, "BROKEN", status
        elif 500 <= status < 600:
            return url, "SERVER_ERROR", status
        else:
            return url, "UNKNOWN", status

    except httpx.TimeoutException:
        return url, "TIMEOUT", None
    except httpx.ConnectError:
        return url, "CONNECTION_FAILED", None
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
    print(f"🚀 Starting Production-Grade Scan | {start_url}\n")

    base_domain = get_domain(start_url)
    visited_pages: Set[str] = set()
    page_queue: asyncio.Queue = asyncio.Queue()
    resource_map = {}

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
                res = await page.goto(current_url, timeout=50000, wait_until="domcontentloaded")
                if res.status >= 400:
                    safe_name = safe_filename(current_url)
                    path = os.path.join(screenshots_dir, f"{safe_name}_{res.status}.png")
                    await page.screenshot(path=path, full_page=True)
                    print(f"{current_url} is Broken | Proof saved to path.")

                await page.wait_for_load_state("domcontentloaded", timeout=20000)

                # === KEY IMPROVEMENT: Reveal dropdowns before extracting ===
                resources = await reveal_dropdowns_and_extract(page)

                # Collect resources
                for resource_type, urls in resources.items():

                    for raw_url in urls:

                        norm = normalize(
                            current_url,
                            raw_url
                        )

                        if not norm:
                            continue

                        if norm not in resource_map:

                            resource_map[norm] = {
                                "found_on": current_url,
                                "resource_type": resource_type
                            }

                # Discover new internal pages
                for link in resources.get("links", []):
                    norm_link = normalize(current_url, link)
                    if norm_link and is_internal(base_domain, norm_link):
                        if norm_link not in visited_pages:
                            if is_html_page(norm_link):
                                await page_queue.put(norm_link)

                await page.close()

            except Exception as e:
                print(f"   ⚠️ Error on {current_url}: {str(e)[:80]}")
            finally:
                page_queue.task_done()

        await browser.close()

    print(f"\n✅ Crawled {len(visited_pages)} pages")
    print(f"📦 Found {len(resource_map)} unique resources\n")

    # Check resources
    print("🔍 Checking all resources for broken items...\n")
    async with httpx.AsyncClient(follow_redirects=True, timeout=TIMEOUT) as client:
        queue: asyncio.Queue = asyncio.Queue()
        results: List[Tuple] = []

        for url in resource_map:
            await queue.put(url)

        workers = [asyncio.create_task(worker(queue, client, results)) for _ in range(CONCURRENCY)]
        await queue.join()
        for _ in workers:
            await queue.put(None)
        await asyncio.gather(*workers, return_exceptions=True)

        all_results = results

        detailed_results = []

        for url, status, code in all_results:
            meta = resource_map.get(
                url,
                {}
            )
            detailed_results.append({
                "url": url,
                "status": status,
                "http_code": code,
                "found_on": meta.get(
                    "found_on"
                ),
                "resource_type": meta.get(
                    "resource_type"
                )
            })

    # Analysis
    ok = [r for r in all_results if r[1] == "OK"]
    redirects = [r for r in all_results if r[1] == "REDIRECT"]
    
    # 1. Expand broken to include connection failures, timeouts, and server crashes
    broken_statuses = {"BROKEN", "SERVER_ERROR", "CONNECTION_FAILED", "TIMEOUT", "ERROR"}
    broken = [r for r in detailed_results if r["status"] in broken_statuses]

    # 2. Fix categorization to use the exact resource_type tracked by the crawler
    broken_images = [b for b in broken if b["resource_type"] in ["images", "posters", "pictures"]]
    broken_links = [b for b in broken if b["resource_type"] == "links"]
    broken_other = [b for b in broken if b["resource_type"] not in ["links", "images", "posters", "pictures"]]

    # Report
    print("=" * 70)
    print("📊 PRODUCTION-GRADE BROKEN RESOURCE REPORT")
    print("=" * 70)
    print(f"Pages crawled:          {len(visited_pages)}")
    print(f"Total resources found:  {len(all_results)}")
    print(f"✅ OK:                  {len(ok)}")
    print(f"🔀 Redirects:           {len(redirects)}")
    print(f"❌ BROKEN:              {len(broken)}")
    print("-" * 70)

    if broken:
        print(f"\n❌ BROKEN RESOURCES ({len(broken)}):")
        for item in broken:
            # Accessing dictionary keys
            print(f"   [{item['http_code'] or item['status']}] {item['url']} (Found on: {item['found_on']})")

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
            "broken_images": len(broken_images),
            "broken_links": len(broken_links)
        },
        "broken_resources": broken
    }

    return response


# =========================
# RUN
# =========================
if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5500/ETHOWT/TESTING/Website-5/index.html"

    result = asyncio.run(scan_site(target))

    print("\n📦 FINAL JSON RESPONSE:\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))