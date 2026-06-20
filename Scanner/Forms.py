#!/usr/bin/env python3
from typing import List, Dict

class FormAuditor:
    def audit_structural_risks(self, pages: List[Dict]) -> List[Dict]:
        """Filters pages with forms and checks for common errors (e.g. missing action targets)."""
        form_heavy_pages = [p for p in pages if p["forms_count"] > 0]
        anomalies = []

        for p in form_heavy_pages:
            for f in p["forms_spec"]:
                if not f["action"]:
                    anomalies.append({
                        "url": p["url"],
                        "issue": "Empty Form Action attribute detected",
                        "method": f["method"]
                    })
        return anomalies