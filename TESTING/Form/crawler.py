"""
crawler.py
Website crawler using BFS to discover internal pages with forms.
Respects max_pages, max_depth, ignores external, mailto, tel, javascript, PDFs, images, social links.
"""

import asyncio
from collections import deque
from urllib.parse import urljoin, urlparse, urlunparse
from typing import Set, List, Tuple, Optional
from playwright.async_api import Page, BrowserContext

# Patterns to ignore
IGNORE_SCHEMES = ("mailto:", "tel:", "javascript:", "data:")
IGNORE_EXTENSIONS = (".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".ico", ".zip", ".rar")
SOCIAL_DOMAINS = (
    "facebook.com", "twitter.com", "x.com", "linkedin.com", "instagram.com",
    "youtube.com", "tiktok.com", "pinterest.com", "reddit.com", "whatsapp.com",
    "telegram.me", "t.me"
)


def normalize_url(url: str) -> str:
    """Remove fragment and normalize."""
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, ""))


def is_internal_url(base_url: str, target_url: str) -> bool:
    """Check if target is same domain/subdomain as base."""
    try:
        base_netloc = urlparse(base_url).netloc.lower()
        target_netloc = urlparse(target_url).netloc.lower()
        if not target_netloc:
            return True  # relative URL
        return target_netloc == base_netloc or target_netloc.endswith("." + base_netloc)
    except Exception:
        return False


def should_ignore_url(url: str) -> bool:
    """Return True if URL should be skipped."""
    url_lower = url.lower().strip()

    if any(url_lower.startswith(s) for s in IGNORE_SCHEMES):
        return True

    parsed = urlparse(url_lower)
    path = parsed.path.lower()

    if any(path.endswith(ext) for ext in IGNORE_EXTENSIONS):
        return True

    # Social / external share links
    if any(social in parsed.netloc for social in SOCIAL_DOMAINS):
        return True

    # Common non-page links
    if any(x in url_lower for x in ["#", "login", "signup", "cart", "checkout"]):
        # We still want to test login/signup forms usually, so don't ignore them here
        # Only ignore if they are clearly external social
        pass

    return False


async def get_internal_links(page: Page, base_url: str) -> List[str]:
    """Extract all internal anchor hrefs from current page."""
    links = set()
    try:
        anchors = page.locator("a[href]")
        count = await anchors.count()
        for i in range(min(count, 500)):  # Safety limit
            try:
                href = await anchors.nth(i).get_attribute("href")
                if not href:
                    continue
                absolute = urljoin(page.url, href)
                normalized = normalize_url(absolute)

                if is_internal_url(base_url, normalized) and not should_ignore_url(normalized):
                    links.add(normalized)
            except Exception:
                continue
    except Exception:
        pass
    return list(links)


async def crawl_site(
    context: BrowserContext,
    root_url: str,
    max_pages: int = 50,
    max_depth: int = 3
) -> List[str]:
    """
    BFS crawl starting from root_url.
    Returns list of unique internal URLs to test (up to limits).
    """
    visited: Set[str] = set()
    pending: deque = deque()
    results: List[str] = []

    normalized_root = normalize_url(root_url)
    pending.append((normalized_root, 0))  # (url, depth)
    visited.add(normalized_root)

    base_domain = urlparse(normalized_root).netloc

    while pending and len(results) < max_pages:
        current_url, depth = pending.popleft()

        if depth > max_depth:
            continue

        results.append(current_url)

        if depth == max_depth:
            continue

        # Open page to extract links
        page = await context.new_page()
        try:
            await page.goto(current_url, wait_until="domcontentloaded", timeout=15000)
            await page.wait_for_timeout(800)  # small settle time

            new_links = await get_internal_links(page, root_url)

            for link in new_links:
                if link not in visited and len(visited) < max_pages * 2:
                    visited.add(link)
                    pending.append((link, depth + 1))
        except Exception as e:
            print(f"[crawler] Failed to crawl {current_url}: {str(e)[:80]}")
        finally:
            await page.close()

    # Always include root even if crawl fails
    if normalized_root not in results:
        results.insert(0, normalized_root)

    return results[:max_pages]