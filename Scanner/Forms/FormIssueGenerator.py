#!/usr/bin/env python3
from typing import Dict, Any, List
from Scanner.Forms.FormResult import FormResult

class FormIssueGenerator:
    """
    Responsibility: Converts failed results into high-fidelity actionable developer issues.
    """
    def generate_issues(self, form_type: str, url: str, result: FormResult) -> List[Dict[str, Any]]:
        """
        Evaluates a FormResult state to generate CriticalIssue or WarningIssue definitions.
        """
        issues = []
        if result.success:
            return issues

        # Classify severity based on form identity and failure type context
        for error in result.errors:
            error_lower = error.lower()
            
            # 1. CRITICAL ISSUE: Form targets that drop/block primary entry pathways
            if form_type in ["LOGIN", "CONTACT"] or "failed to locate" in error_lower or "crash" in error_lower:
                issues.append({
                    "issue_type": "CriticalIssue",
                    "url": url,
                    "form_type": form_type,
                    "summary": f"Functional pipeline failure detected inside mission-critical {form_type} element.",
                    "details": error,
                    "reproduction_proof": result.messages
                })
            
            # 2. WARNING ISSUE: Auxiliary or non-blocking issues
            else:
                issues.append({
                    "issue_type": "WarningIssue",
                    "url": url,
                    "form_type": form_type,
                    "summary": f"Non-blocking layout or structural validation discrepancy on {form_type} block.",
                    "details": error,
                    "reproduction_proof": result.messages
                })
                
        return issues