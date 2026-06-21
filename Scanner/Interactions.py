#!/usr/bin/env python3
import logging
from playwright.async_api import Page, Locator
from typing import List, Set, Callable, Awaitable

logger = logging.getLogger(__name__)

class InteractionEngine:
    def __init__(self, max_interactions_per_page: int = 30):
        self.max_interactions = max_interactions_per_page

    async def reveal_hidden_dom(self, page: Page, nodes: List[Locator], nav_extractor, callback_on_delta: Callable[[], Awaitable[None]]):
        """
        Systematically audits all discovery candidate nodes and logs distinct 
        contextual actions to maximize target state transparency.
        """
        seen_signatures: Set[str] = set()
        executed_count = 0
        initial_url = page.url

        for i, node in enumerate(nodes):
            if executed_count >= self.max_interactions:
                print(f"   [INFO] Reached maximum runtime execution threshold limit ({self.max_interactions}).")
                break

            if page.url != initial_url:
                print(f"   [🔄 RECOVERY] State mismatch verified before element #{i}. Triggering history step-back...")
                try:
                    await page.go_back(wait_until="domcontentloaded", timeout=5000)
                    await page.wait_for_timeout(400)
                    if page.url != initial_url:
                        print("   [🛑 CRITICAL] Failed to reconstruct position via page history context. Exiting loop.")
                        break
                except Exception as err:
                    print(f"   [🛑 CRITICAL] Redirection tracking recovery failed: {err}")
                    break

            try:
                if not await node.is_visible(): 
                    continue
                    
                sig = await nav_extractor.extract_element_signature(node)
                if not sig or sig in seen_signatures: 
                    continue
                seen_signatures.add(sig)

                tag = await node.evaluate("el => el.tagName.toLowerCase()")
                input_type = (await node.get_attribute("type") or "").lower()
                cls = (await node.get_attribute("class") or "").strip().replace("\n", " ")
                cls_summary = f" class='{cls}'" if cls else ""

                # 2. Structured Action Context Dispatcher
                # Context A: Forms Field Handling
                if tag == "textarea" or (tag == "input" and input_type in ["text", "email", "tel", "url", "number", "password"]):
                    print(f"   [🎯 AUDIT #{i}] Text Element -> <{tag} type='{input_type}'>{cls_summary}")
                    await node.focus()
                    await node.fill("WebSentinel_Validation_Payload")
                    await page.wait_for_timeout(100)
                    executed_count += 1
                    continue

                # Context B: Toggle Elements Handling
                elif tag == "input" and input_type in ["checkbox", "radio"]:
                    print(f"   [🎯 AUDIT #{i}] Selection Toggle Element -> <input type='{input_type}'>{cls_summary}")
                    await node.check(timeout=300)
                    executed_count += 1
                    await callback_on_delta()
                    continue

                # Context C: Selection Fields Handling
                elif tag == "select":
                    options = await node.evaluate("""sel => Array.from(sel.options).map(o => o.value).filter(Boolean)""")
                    if options:
                        print(f"   [🎯 AUDIT #{i}] Selection Dropdown Node -> <select value='{options[0]}'>{cls_summary}")
                        await node.select_option(value=options[0])
                        executed_count += 1
                        await callback_on_delta()
                    continue

                # Context D: Fallthrough General Interactive UI Node Handler
                else:
                    print(f"   [🎯 AUDIT #{i}] Structural UI Element -> <{tag}>{cls_summary}")
                    await node.click(timeout=500, no_wait_after=True)
                    await page.wait_for_timeout(500)
                    executed_count += 1

                    if page.url == initial_url:
                        await callback_on_delta()
                    else:
                        print(f"      [↪️ REDIRECT] Action triggered domain path navigation change to: {page.url}")
                        await page.go_back(wait_until="domcontentloaded", timeout=5000)
                        await page.wait_for_timeout(300)

                try:
                    await page.keyboard.press("Escape")
                except: 
                    pass
                    
            except Exception as node_err:
                logger.debug(f"Target verification element skipped during iteration pipeline: {node_err}")
                continue

if __name__ == "__main__":
    import asyncio
    from playwright.async_api import async_playwright, Page

    from LinkExtractor import LinkExtractor
    from NavigationExtractor import NavigationExtractor

    async def on_delta_notification():
        print("   [CALLBACK] -> Mutation observer matched layout structural shift.")

    async def run_comprehensive_audit():
        TARGET_URL = "http://127.0.0.1:5501/TESTING/Website-5/contact.html"
        
        linker = LinkExtractor(base_url=TARGET_URL)
        nav_extractor = NavigationExtractor()
        engine = InteractionEngine(max_interactions_per_page=25)

        async with async_playwright() as p:
            print(f"Initializing WebSentinel Test Environment for target: {TARGET_URL}")
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(TARGET_URL, wait_until="networkidle")

                print("\n--- PRE-SEEDING FORM FIELDS FOR VALIDATION VALIDITY ---")
                inputs = await page.locator("input[type='text'], input[type='email'], textarea").all()
                for i, field in enumerate(inputs):
                    if await field.is_visible():
                        tag = await field.evaluate("el => el.tagName.toLowerCase()")
                        print(f"  -> Seeding input control #{i} <{tag}> with testing string data...")
                        await field.fill("WebSentinel_Automation_Testing")

                candidates = await nav_extractor.locate_interactive_nodes(page)
                print(f"\nDiscovered {len(candidates)} functional element interaction paths across target page DOM.")

                print("\n=== STARTING SYSTEM INTEGRATION LIFECYCLE ===")
                await engine.reveal_hidden_dom(page=page, nodes=candidates, nav_extractor=nav_extractor, callback_on_delta=on_delta_notification)
                print("=== SYSTEM INTEGRATION LIFECYCLE FINISHED ===")

            except Exception as err:
                print(f"Automation execution run failed: {err}")
            finally:
                await browser.close()
    asyncio.run(run_comprehensive_audit())