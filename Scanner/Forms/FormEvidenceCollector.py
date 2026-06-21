#!/usr/bin/env python3
import os
import uuid
import logging
from playwright.async_api import Page
from typing import Optional

logger = logging.getLogger(__name__)

class FormEvidenceCollector:
    """
    Responsibility: Persists diagnostic data objects (screenshots, active trace definitions, logs) to physical disk storage.
    """
    def __init__(self, output_dir: str = "Evidence/Forms"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    async def collect_page_snapshot(self, page: Page, form_type: str) -> Optional[str]:
        """
        Saves a physical binary image file snapshot of the browser frame for reporting proof.
        """
        try:
            filename = f"{form_type.lower()}_failure_{uuid.uuid4().hex[:8]}.png"
            file_path = os.path.join(self.output_dir, filename)
            
            # Capture the current live frame buffer
            await page.screenshot(path=file_path, full_page=False)
            logger.info(f"FormEvidenceCollector successfully generated binary image footprint trace: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Failed to generate evidence snapshot asset: {e}")
            return None