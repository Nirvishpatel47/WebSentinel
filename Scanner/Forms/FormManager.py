#!/usr/bin/env python3
import logging
import time
from playwright.async_api import Page
from typing import List, Dict, Any

# Core component pipelines dependencies mapping matching your modular architecture
from Scanner.Forms.FormExtractor import FormExtractor
from Scanner.Forms.FormFieldExtractor import FormFieldExtractor
from Scanner.Forms.FormClassifier import FormClassifier
from Scanner.Forms.StrategyFactory import StrategyFactory
from Scanner.Forms.FormResult import FormResult
from Scanner.Forms.FormIssueGenerator import FormIssueGenerator
from Scanner.Forms.FormEvidenceCollector import FormEvidenceCollector

logger = logging.getLogger(__name__)

class FormManager:
    """
    Responsibility: Orchestrates the entire form pipeline lifecycle.
    Flow: FormExtractor -> FormFieldExtractor -> FormClassifier -> StrategyFactory -> SpecificTester -> Result -> IssueGen -> Evidence.
    """
    def __init__(self):
        self.extractor = FormExtractor()
        self.field_extractor = FormFieldExtractor()
        self.classifier = FormClassifier()
        self.issue_generator = FormIssueGenerator()
        self.evidence_collector = FormEvidenceCollector()

    async def process_page_forms(self, page: Page, url: str) -> Dict[str, Any]:
        """
        Orchestrates pipeline components over a web document without executing manual testing inside itself.
        """
        page_issues = []
        page_results = []

        logger.info(f"FormManager initiating unified orchestration pipeline on location: {url}")
        
        # Step 1: FormExtractor -> Locate all explicit form elements
        form_locators = await self.extractor.locate_forms(page)
        
        for index, form_loc in enumerate(form_locators):
            try:
                action = await form_loc.get_attribute("action") or ""
                method = (await form_loc.get_attribute("method") or "GET").upper()

                # Step 2: FormFieldExtractor -> Interrogate internal attributes and elements
                fields_spec = await self.field_extractor.extract_fields(form_loc)

                # Step 3: FormClassifier -> Classify operational intent
                form_type = self.classifier.classify(action, method, fields_spec)

                # Step 4 & 5: StrategyFactory -> Fetch dedicated specific tester runner context
                tester_strategy = StrategyFactory.get_tester(form_type)
                
                # Step 6: SpecificFormTester Run -> Execute inputs simulation and parse verification dictionary
                raw_test_data = await tester_strategy.test(page, form_loc, fields_spec)

                # Collect structural visual evidence if the specific verification sequence reports faults
                screenshot_path = None
                if not raw_test_data["success"]:
                    screenshot_path = await self.evidence_collector.collect_page_snapshot(page, form_type)

                # Step 7: FormResult -> Package into standard tracking results model
                result_object = FormResult(
                    success=raw_test_data["success"],
                    errors=raw_test_data["errors"],
                    messages=raw_test_data["messages"],
                    timings=raw_test_data["timings"],
                    screenshot_path=screenshot_path
                )
                page_results.append({f"form_{index}_{form_type}": result_object.to_dict()})

                # Step 8: FormIssueGenerator -> Map failures to Critical or Warning issues schema
                discovered_issues = self.issue_generator.generate_issues(form_type, url, result_object)
                page_issues.extend(discovered_issues)

            except Exception as loop_err:
                logger.error(f"FormManager dropped orchestration step at position index #{index}: {loop_err}")
                continue

        return {
            "url": url,
            "total_forms_audited": len(form_locators),
            "results": page_results,
            "anomalies": page_issues
        }