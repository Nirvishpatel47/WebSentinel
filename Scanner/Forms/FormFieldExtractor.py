#!/usr/bin/env python3
from playwright.async_api import Locator
from typing import List, Dict, Any

class FormFieldExtractor:
    """
    Extracts all fields from an individual form locator element.
    Output data structure maps cleanly into the downstream FormClassifier.
    """
    async def extract_fields(self, form_locator: Locator) -> List[Dict[str, Any]]:
        """
        Queries all field tags inside the form element and extracts their properties.
        """
        try:
            # Execute precise extraction inside the browser execution context
            return await form_locator.evaluate("""
                (form) => {
                    const fields = Array.from(form.querySelectorAll('input, select, textarea, button'));
                    return fields.map(field => {
                        const tagName = field.tagName.toLowerCase();
                        const typeAttr = (field.getAttribute('type') || '').toLowerCase();
                        
                        // Parse options for select elements
                        let selectOptions = [];
                        if (tagName === 'select') {
                            selectOptions = Array.from(field.options).map(o => o.value || o.text).filter(Boolean);
                        }

                        return {
                            tag: tagName,
                            type: typeAttr || (tagName === 'textarea' ? 'textarea' : tagName),
                            name: field.getAttribute('name') || field.getAttribute('id') || '',
                            id: field.id || '',
                            placeholder: field.getAttribute('placeholder') || '',
                            required: field.hasAttribute('required'),
                            value: field.value || field.getAttribute('value') || '',
                            options: selectOptions
                        };
                    });
                }
            """)
        except Exception as e:
            # Return empty array if the node is detached or mutated during evaluation
            return []