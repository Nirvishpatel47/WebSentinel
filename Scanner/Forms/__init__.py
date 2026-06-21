"""
FORMS MODULE ARCHITECTURE
=========================

One file = One class = One responsibility

FormExtractor.py
----------------
Responsibility:
    Discover forms from pages.

Input:
    Page

Output:
    List[DiscoveredForm]


FormFieldExtractor.py
---------------------
Responsibility:
    Extract fields from a form.

Input:
    HTML form element

Output:
    List[Field]


FormClassifier.py
-----------------
Responsibility:
    Determine form type.

Input:
    DiscoveredForm

Output:
    CONTACT
    NEWSLETTER
    LOGIN
    SEARCH
    QUOTE
    BOOKING
    UNKNOWN


StrategyFactory.py
------------------
Responsibility:
    Return correct tester.

Input:
    FormType

Output:
    ContactFormTester
    NewsletterFormTester
    LoginFormTester
    SearchFormTester
    UnknownFormTester


ContactFormTester.py
--------------------
Responsibility:
    Test contact forms.

Actions:
    Fill fields
    Submit
    Detect success/error


NewsletterFormTester.py
-----------------------
Responsibility:
    Test newsletter forms.


LoginFormTester.py
------------------
Responsibility:
    Test login forms.

Actions:
    Verify fields
    Verify validation

(No actual login)


SearchFormTester.py
-------------------
Responsibility:
    Test search forms.

Actions:
    Search test query
    Verify results page


UnknownFormTester.py
--------------------
Responsibility:
    Safely test unknown forms.

Actions:
    Minimal interaction
    Avoid dangerous submissions


FormResult.py
--------------
Responsibility:
    Store testing results.

Contains:
    success
    errors
    screenshots
    messages
    timings


FormIssueGenerator.py
---------------------
Responsibility:
    Convert failed results into issues.

Output:
    CriticalIssue
    WarningIssue


FormEvidenceCollector.py
------------------------
Responsibility:
    Save screenshots, traces, logs.


FormManager.py
--------------
Responsibility:
    Orchestrate the entire form pipeline.

Flow:

FormExtractor
        ↓
FormFieldExtractor
        ↓
FormClassifier
        ↓
StrategyFactory
        ↓
SpecificFormTester
        ↓
FormResult
        ↓
FormIssueGenerator
        ↓
FormEvidenceCollector

FormManager itself does NOT test forms.
It only coordinates the pipeline.
"""