#!/usr/bin/env python3

import logging
from typing import Dict, Any

from playwright.async_api import Page

from Scanner.Forms.FormExtractor import FormExtractor
from Scanner.Forms.FormClassifier import FormClassifier
from Scanner.Forms.StrategyFactory import StrategyFactory
from Scanner.Forms.FormIssueGenerator import FormIssueGenerator
from Scanner.Forms.FormEvidenceCollector import Evidence

logger = logging.getLogger(__name__)


class FormManager:
    """
    Responsibility:
        Orchestrate the form pipeline.

    Flow:

        FormExtractor
            ↓
        FormClassifier
            ↓
        StrategyFactory
            ↓
        Specific Tester
            ↓
        FormResult
            ↓
        Evidence Collector
            ↓
        FormIssueGenerator
    """

    def __init__(self):
        self.extractor = FormExtractor()
        self.classifier = FormClassifier()
        self.factory = StrategyFactory()
        self.issue_generator = FormIssueGenerator()
        self.evidence_collector = Evidence

    async def process_page_forms(
        self,
        page: Page,
        url: str
    ) -> Dict[str, Any]:

        page_results = []
        page_issues = []

        logger.info(
            f"Processing forms for {url}"
        )

        try:
            forms = await self.extractor.extract_forms(page)

        except Exception as e:
            logger.exception(
                f"Failed extracting forms from {url}: {e}"
            )

            return {
                "url": url,
                "total_forms_audited": 0,
                "results": [],
                "anomalies": []
            }

        for index, form in enumerate(forms):

            try:
                action = form.get("action", "")
                method = form.get("method", "GET")
                fields = form.get("fields", [])
                form_locator = form.get("locator")

                # ---------- classify ----------
                form_type = self.classifier.classify(
                    action,
                    method,
                    fields
                )

                # ---------- tester ----------
                tester = self.factory.get_tester(
                    form_type
                )

                result = await tester.test(
                    page,
                    form_locator,
                    fields
                )

                # ---------- evidence ----------
                """ if not result.success:

                    screenshot_path = (
                        await self.evidence_collector.capture_form_snapshot(
                            page,
                            form_type,
                            "None"
                        )
                    )

                    if screenshot_path:
                        result.screenshots.append(
                            screenshot_path
                        ) """

                # ---------- store result ----------
                page_results.append({
                    "form_index": index,
                    "form_type": form_type,
                    "result": result.to_dict()
                })

                # ---------- issue generation ----------
                issues = (
                    self.issue_generator.generate_issues(
                        form_type,
                        url,
                        result
                    )
                )

                page_issues.extend(
                    issues
                )

            except Exception as e:

                logger.exception(
                    f"Failed processing form #{index}: {e}"
                )

        return {
            "url": url,
            "total_forms_audited": len(forms),
            "results": page_results,
            "anomalies": page_issues
        }