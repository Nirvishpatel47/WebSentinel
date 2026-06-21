#!/usr/bin/env python3
import asyncio
from urllib.parse import urlparse
from Browser import BrowserManager
from LinkExtractor import LinkExtractor
from ResourceExtractor import ResourceExtractor
from FormExtractor import FormExtractor
from NavigationExtractor import NavigationExtractor
from Interactions import InteractionEngine

class SentinelCrawler:
    def __init__(self, start_url: str, max_pages: int = 40, max_depth: int = 3):
        self.start_url = start_url
        self.max_pages = max_pages
        self.max_depth = max_depth

        # Core Engines
        self.browser_mgr = BrowserManager()
        self.linker = LinkExtractor(start_url)
        self.res_extractor = ResourceExtractor()
        self.form_extractor = FormExtractor()
        self.nav_extractor = NavigationExtractor()
        self.interactor = InteractionEngine()

        # Operational Registries
        self.visited_pages = set()
        self.pages_metadata = []
        self.global_resources = {}
        self.errors = []
        
        self.html_exclusions = (".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".css", ".js", ".zip")

    def is_html_route(self, url: str) -> bool:
        return not urlparse(url).path.lower().endswith(self.html_exclusions)

    async def execute(self) -> dict:
        print(f"🛰️  Starting WebSentinel Crawl Loop on: {self.linker.base_domain}")
        context = await self.browser_mgr.init_session()
        
        queue = asyncio.Queue()
        root_url = self.linker.canonicalize(self.start_url)
        await queue.put((root_url, 0))

        while not queue.empty() and len(self.visited_pages) < self.max_pages:
            current_url, depth = await queue.get()

            if current_url in self.visited_pages or depth > self.max_depth:
                queue.task_done()
                continue

            self.visited_pages.add(current_url)
            print(f"🔹 [Depth {depth}][Visited {len(self.visited_pages)}] Indexing: {current_url}")

            page = None
            try:
                page = await context.new_page()
                
                network_urls = set()
                page.on("response", lambda r: network_urls.add(r.url) if any(r.url.lower().startswith(s) for s in ["http", "https"]) else None)

                response = await page.goto(current_url, timeout=30000, wait_until="domcontentloaded")
                if response.status >= 400:
                    await self.browser_mgr.take_screenshot(page, current_url, response.status)

                await page.wait_for_load_state("domcontentloaded", timeout=10000)

                # 1. Base Static Capture Layer
                base_links = await self.linker.extract(page, current_url)
                internal_links = base_links["internal"]
                external_links = base_links["external"]
                
                dom_assets = await self.res_extractor.extract_dom_resources(page)
                forms_list = await self.form_extractor.extract_forms(page)
                interactive_nodes = await self.nav_extractor.locate_interactive_nodes(page)

                # 2. Dynamic Capture Handler via Delta Updates Callback
                async def on_dom_mutation():
                    nonlocal internal_links, external_links
                    delta_links = await self.linker.extract(page, current_url)
                    internal_links.update(delta_links["internal"])
                    external_links.update(delta_links["external"])
                    
                    delta_assets = await self.res_extractor.extract_dom_resources(page)
                    for cat, paths in delta_assets.items():
                        dom_assets[cat].extend(paths)

                await self.interactor.reveal_hidden_dom(page, interactive_nodes, self.nav_extractor, on_dom_mutation)

                # 3. Process Global Resource Mapping Tables
                self.res_extractor.map_to_global(current_url, dom_assets, network_urls, self.global_resources, self.linker)

                # 4. Schedule discovered internal routes
                for link in internal_links:
                    if link not in self.visited_pages and self.is_html_route(link):
                        await queue.put((link, depth + 1))

                title = await page.title() if not page.is_closed() else ""
                
                # 5. Build Pristine Structured Page Metadata Object
                self.pages_metadata.append({
                    "url": current_url,
                    "depth": depth,
                    "title": title,
                    "forms_count": len(forms_list),
                    "forms_spec": forms_list,
                    "dropdown_count": len(interactive_nodes),
                    "internal_links": sorted(list(internal_links)),
                    "external_links": sorted(list(external_links))
                })

            except Exception as e:
                print(f"⚠️  Crawl error processing [{current_url}]: {e}")
                self.errors.append({"url": current_url, "error": str(e)})
            finally:
                if page: await page.close()
                queue.task_done()

        await self.browser_mgr.close_session()
        return {
            "success": True,
            "root": self.start_url,
            "page_count": len(self.pages_metadata),
            "pages": self.pages_metadata,
            "resources": self.global_resources,
            "errors": self.errors
        }