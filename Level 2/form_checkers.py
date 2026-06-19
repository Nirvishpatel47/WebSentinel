import asyncio
from playwright.async_api import async_playwright


TEST_DATA = {
    "name": "John Doe",
    "email": "qa-test@example.com",
    "phone": "9876543210",
    "company": "QA Automation Ltd",
    "job_title": "QA Engineer",
    "message": "This is an automated QA test submission.",
    "password": "Password@123",
    "unknown": "Test Value"
}


def classify_field(field):
    text = " ".join(
        str(x).lower()
        for x in [
            field.get("name"),
            field.get("id"),
            field.get("placeholder"),
            field.get("label"),
            field.get("aria_label"),
            field.get("type")
        ]
        if x
    )

    if "email" in text:
        return "email"

    if "password" in text:
        return "password"

    if any(x in text for x in ["phone", "mobile", "tel", "telephone"]):
        return "phone"

    if any(x in text for x in ["company", "business", "organization", "firm"]):
        return "company"

    if any(x in text for x in ["role", "designation", "title", "position", "job", "occupation"]):
        return "job_title"

    if any(x in text for x in ["message", "comment", "description", "details", "requirements", "notes", "feedback", "query", "question project"]):
        return "message"

    if "name" in text:
        return "name"

    return "unknown"


async def get_field_info(field):
    tag = await field.evaluate(
        "el => el.tagName.toLowerCase()"
    )

    field_id = await field.get_attribute("id")

    label_text = None

    if field_id:
        page = field.page

        label = page.locator(f'label[for="{field_id}"]')

        if await label.count():
            label_text = await label.first.text_content()

    return {
        "tag": tag,
        "type": await field.get_attribute("type"),
        "name": await field.get_attribute("name"),
        "id": field_id,
        "placeholder": await field.get_attribute("placeholder"),
        "required": await field.get_attribute("required") is not None,
        "aria_label": await field.get_attribute("aria-label"),
        "label": label_text
    }


async def fill_field(locator, field_type):
    value = TEST_DATA.get(field_type, TEST_DATA["unknown"])

    tag = await locator.evaluate("el => el.tagName.toLowerCase()")

    if tag in ["input", "textarea"]:
        await locator.fill(value)
        return

    if tag == "select":
        options = await locator.locator("option").count()

        if options > 1:
            try:
                await locator.select_option(index=1)
            except Exception:
                pass

async def find_submit_button(form):
    selectors = [
        'button[type="submit"]',
        'input[type="submit"]',
        'button'
    ]

    for selector in selectors:
        buttons = form.locator(selector)

        count = await buttons.count()

        for i in range(count):
            button = buttons.nth(i)

            try:
                text = (await button.text_content() or "").strip().lower()

                button_type = ( await button.get_attribute("type") or "" ).lower()

                if button_type == "submit":
                    return button

                if any(word in text for word in ["submit", "send", "contact", "register", "sign up", "continue", "apply", "save"]):
                    return button

            except Exception:
                pass

    return None

async def detect_result(page, old_url):
    content = (await page.text_content("body") or "").lower()

    success_patterns = [
        "thank you",
        "success",
        "submitted",
        "message sent",
        "form submitted",
        "received"
    ]

    error_patterns = [
        "required",
        "invalid",
        "error",
        "please enter",
        "field is required"
    ]

    result = {
        "success": False,
        "url_changed": False,
        "success_text": None,
        "error_text": None
    }

    if page.url != old_url:
        result["url_changed"] = True

    for pattern in success_patterns:
        if pattern in content:
            result["success"] = True
            result["success_text"] = pattern
            return result

    for pattern in error_patterns:
        if pattern in content:
            result["error_text"] = pattern
            return result

    if result["url_changed"]:
        result["success"] = True

    return result

async def process_page(url):
    async with async_playwright() as p:

        browser = await p.chromium.launch(headless=True)

        page = await browser.new_page()

        await page.goto(url, wait_until="networkidle")

        forms = page.locator("form")

        form_count = await forms.count()

        print(f"\nForms Found | {form_count}")

        for form_index in range(form_count):

            print(f"\nFORM  | {form_index}")

            form = forms.nth(form_index)

            fields = form.locator("input, textarea, select")

            field_count = await fields.count()

            for field_index in range(field_count):

                locator = fields.nth(field_index)

                info = await get_field_info(locator)

                field_type = classify_field(info)

                print(f"Field | {field_index} | " f"{field_type}")

                try:
                    await fill_field(locator, field_type)
                except Exception as e:
                    print(f"Fill Failed: {e}")

            submit_btn = await find_submit_button(form)

            if not submit_btn:
                print("No submit button found.")
                continue

            print("Submit button found.")

            old_url = page.url

            try:
                await submit_btn.click(timeout=5000)

                await page.wait_for_timeout(3000)

            except Exception as e:
                print(f"Submit failed: {e}")
                continue

            result = await detect_result(page, old_url)

            print("\nRESULT")
            print(result)

        await page.wait_for_timeout(5000)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(process_page("http://127.0.0.1:5500/ETHOWT/TESTING/Website-5/contact.html"))