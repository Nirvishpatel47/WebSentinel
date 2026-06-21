#!/usr/bin/env python3
from typing import List, Dict

class FormAuditor:
    def audit_structural_risks(self, pages: List[Dict]) -> List[Dict]:
        """Analyzes compiled page data schemas to surface operational or security vulnerabilities."""
        form_heavy_pages = [p for p in pages if p.get("forms_count", 0) > 0]
        anomalies = []

        for p in form_heavy_pages:
            current_url = p.get("url", "Unknown URL")
            forms_list = p.get("forms_spec", [])

            for f in forms_list:
                action = f.get("action", "").strip()
                method = f.get("method", "GET").upper()
                inputs = f.get("inputs", [])

                # 1. Structural Check: Check for Empty Actions
                if not action:
                    anomalies.append({
                        "url": current_url,
                        "issue": "Empty Form Action attribute detected",
                        "severity": "LOW",
                        "method": method
                    })
                
                # Check for sensitive fields to drive context-aware auditing
                has_password_field = any(i.get("type", "").lower() == "password" for i in inputs)

                if has_password_field:
                    # 2. Security Check: Cleartext transmission over an unencrypted page
                    if current_url.lower().startswith("http://"):
                        anomalies.append({
                            "url": current_url,
                            "issue": "Insecure form context: Sensitive credentials handled over unencrypted HTTP",
                            "severity": "CRITICAL",
                            "method": method
                        })

                    # 3. Security Check: Sensitive fields submitted via GET operations
                    if method == "GET":
                        anomalies.append({
                            "url": current_url,
                            "issue": "Sensitive authentication field submitted via GET query parameters",
                            "severity": "HIGH",
                            "method": method
                        })

        return anomalies
    
if __name__ == "__main__":

    def run_auditor_test():
        mock_scan_results = [
            {
                "url": "https://example.com/login",
                "forms_count": 1,
                "forms_spec": [
                    {
                        "action": "",  
                        "method": "POST",
                        "inputs": [{"type": "text", "name": "user"}, {"type": "password", "name": "pass"}]
                    }
                ]
            },
            {
                "url": "http://insecure-site.org/register",
                "forms_count": 1,
                "forms_spec": [
                    {
                        "action": "/submit-registration",
                        "method": "GET",  # Generates a Sensitive GET warning
                        "inputs": [{"type": "password", "name": "token"}]
                    }
                ]
            },
            {
                "url": "https://example.com/blog/clean-page",
                "forms_count": 0,
                "forms_spec": []  
            }
        ]

        auditor = FormAuditor()
        discovered_issues = auditor.audit_structural_risks(mock_scan_results)

        print(f"=== AUDITOR TEST OUTPUT: FOUND {len(discovered_issues)} ANOMALIES ===")
        for index, issue in enumerate(discovered_issues, 1):
            print(f"\nAnomaly #{index}")
            print(f"  Target URL:  {issue['url']}")
            print(f"  Issue Found: {issue['issue']}")
            print(f"  HTTP Method: {issue['method']}")

    if __name__ == "__main__":
        run_auditor_test()