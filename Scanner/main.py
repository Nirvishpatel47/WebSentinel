#!/usr/bin/env python3
import asyncio
import json
from Crawl import SentinelCrawler
from BrokenLinks import BrokenLinkValidator
from Forms import FormAuditor

async def run_sentinel():
    target_site = "http://127.0.0.1:5501/TESTING/Website-5/index.html"
    
    # 1. Run Page Discovery & Data Extraction
    crawler = SentinelCrawler(target_site, max_pages=50, max_depth=5)
    crawl_report = await crawler.execute()
    
    # 2. Extract specific payloads for subsequent modules
    pages_metadata = crawl_report["pages"]
    discovered_assets = crawl_report["resources"]

    # 3. Validate Links & Hidden Resources
    validator = BrokenLinkValidator(concurrency=15)
    validation_report = await validator.validate_all(discovered_assets)
    
    # 4. Audit Web Form Specifications
    form_auditor = FormAuditor()
    form_anomalies = form_auditor.audit_structural_risks(pages_metadata)

    # Compile Final Consolidated Output
    broken_items = [item for item in validation_report if item["status"] != "OK"]
    
    print("\n" + "="*60)
    print("📊 WEB SENTINEL INTEGRATED AUDIT COMPLETE")
    print("="*60)
    print(f"Total Pages Cataloged:  {crawl_report['page_count']}")
    print(f"Broken Assets Flagged:  {len(broken_items)}")
    print(f"Form Security Faults:   {len(form_anomalies)}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(run_sentinel())