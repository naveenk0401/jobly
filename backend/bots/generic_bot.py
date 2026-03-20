from playwright.async_api import async_playwright, Page
from utils.groq_client import chat_complete
import asyncio

class GenericBot:
    """
    Best-effort form filler for Workday and
    unknown ATS platforms.

    Strategy:
      1. Match inputs by name/placeholder/aria-label
         against known field keywords
      2. Upload resume to first file input found
      3. Answer textareas with Groq
      4. Try multiple submit button selectors
      5. Never crash — wrap everything in try/except
    """

    FIELD_MAP = {
        "first": [
            "first", "firstname", "first_name",
            "given", "fname"
        ],
        "last": [
            "last", "lastname", "last_name",
            "family", "surname", "lname"
        ],
        "email": [
            "email", "e-mail", "emailaddress"
        ],
        "phone": [
            "phone", "mobile", "telephone",
            "cell", "contact"
        ],
    }

    async def apply(
        self,
        job: dict,
        user: dict,
        resume_path: str
    ) -> dict:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            ctx  = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X "
                    "10_15_7) AppleWebKit/537.36"
                )
            )
            page = await ctx.new_page()

            try:
                await page.goto(
                    job["apply_url"], timeout=25000
                )
                # Workday loads slowly
                await page.wait_for_load_state(
                    "networkidle", timeout=20000
                )
                await asyncio.sleep(2)

                name_parts = user.get("name", "").split()
                field_values = {
                    "first": (
                        name_parts[0] if name_parts else ""
                    ),
                    "last":  (
                        name_parts[-1]
                        if len(name_parts) > 1
                        else ""
                    ),
                    "email": user.get("email", ""),
                    "phone": user.get("phone", ""),
                }

                # Fill all text inputs by hint matching
                inputs = await page.query_selector_all(
                    "input[type='text'], "
                    "input[type='email'], "
                    "input[type='tel'], "
                    "input:not([type])"
                )

                for inp in inputs:
                    await self._smart_fill(
                        inp, field_values
                    )

                # Resume upload
                upload = await page.query_selector(
                    "input[type='file']"
                )
                if upload:
                    await upload.set_input_files(resume_path)
                    await asyncio.sleep(2)

                # Custom questions
                textareas = await page.query_selector_all(
                    "textarea"
                )
                for ta in textareas:
                    try:
                        question = (
                            await ta.get_attribute(
                                "aria-label"
                            ) or
                            await ta.get_attribute(
                                "placeholder"
                            ) or ""
                        )
                        if question:
                            answer = await chat_complete(
                                system=(
                                    "Answer job application "
                                    "questions concisely. "
                                    "Max 2 sentences."
                                ),
                                user=(
                                    f"Question: {question}\n"
                                    f"Background: "
                                    f"{user.get('summary','')}"
                                ),
                                max_tokens=100
                            )
                            if answer:
                                await ta.fill(answer)
                                await asyncio.sleep(0.3)
                    except Exception:
                        continue

                # Submit
                submitted = await self._submit(page)
                if not submitted:
                    return {
                        "status": "failed",
                        "error":  "Submit button not found"
                    }

                await page.wait_for_load_state(
                    "networkidle", timeout=15000
                )

            except Exception as e:
                await browser.close()
                return {"status": "failed", "error": str(e)}

            await browser.close()
            return {"status": "applied"}

    async def _smart_fill(self, inp, field_values: dict):
        """
        Fills an input by matching its attributes
        against known field keywords.
        """
        try:
            name  = (
                await inp.get_attribute("name") or ""
            ).lower()
            ph    = (
                await inp.get_attribute("placeholder") or ""
            ).lower()
            aria  = (
                await inp.get_attribute("aria-label") or ""
            ).lower()
            label = (
                await inp.get_attribute("id") or ""
            ).lower()
            hint  = f"{name} {ph} {aria} {label}"

            for field, keywords in self.FIELD_MAP.items():
                if any(kw in hint for kw in keywords):
                    value = field_values.get(field, "")
                    if value:
                        await inp.fill(value)
                    break
        except Exception:
            pass

    async def _submit(self, page: Page) -> bool:
        selectors = [
            # Workday specific
            "[data-automation-id='bottom-navigation-next-button']",
            "[data-automation-id='click_done']",
            # Generic
            "button[type='submit']",
            "input[type='submit']",
            "button:has-text('Submit')",
            "button:has-text('Apply')",
            "button:has-text('Next')",
            "[class*='submit']",
        ]
        for sel in selectors:
            try:
                btn = await page.query_selector(sel)
                if btn:
                    await btn.click()
                    return True
            except Exception:
                continue
        return False
