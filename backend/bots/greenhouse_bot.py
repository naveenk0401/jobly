from playwright.async_api import async_playwright, Page
from utils.groq_client import chat_complete
import asyncio

class GreenhouseBot:
    """
    Applies to jobs on boards.greenhouse.io

    Form structure:
      - first_name: input[name*='first']
      - last_name:  input[name*='last']
      - email:      input[type='email']
      - phone:      input[type='tel']
      - resume:     input[type='file']
      - custom Q&A: textarea elements with labels
      - submit:     #submit_app, button[type='submit']
    """

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
                    job["apply_url"], timeout=20000
                )
                await page.wait_for_load_state("networkidle")

                # Fill standard fields
                name_parts = user.get("name", "").split()
                first = name_parts[0] if name_parts else ""
                last  = (
                    name_parts[-1]
                    if len(name_parts) > 1
                    else ""
                )

                await self._fill(
                    page,
                    "input[name*='first'], "
                    "input[id*='first']",
                    first
                )
                await self._fill(
                    page,
                    "input[name*='last'], "
                    "input[id*='last']",
                    last
                )
                await self._fill(
                    page,
                    "input[type='email'], "
                    "input[name*='email']",
                    user.get("email", "")
                )
                await self._fill(
                    page,
                    "input[type='tel'], "
                    "input[name*='phone']",
                    user.get("phone", "")
                )

                # Resume upload
                upload = await page.query_selector(
                    "input[type='file']"
                )
                if upload:
                    await upload.set_input_files(resume_path)
                    await asyncio.sleep(1)

                # Handle custom questions
                await self._answer_questions(page, user, job)

                # Submit
                submitted = await self._submit(page)
                if not submitted:
                    return {
                        "status": "failed",
                        "error":  "Submit button not found"
                    }

                await page.wait_for_load_state(
                    "networkidle", timeout=10000
                )

            except Exception as e:
                await browser.close()
                return {"status": "failed", "error": str(e)}

            await browser.close()
            return {"status": "applied"}

    async def _fill(
        self, page: Page, selector: str, value: str
    ):
        if not value:
            return
        try:
            el = await page.query_selector(selector)
            if el:
                await el.fill(value)
        except Exception:
            pass

    async def _answer_questions(
        self, page: Page, user: dict, job: dict
    ):
        """
        Finds all visible textareas and fills them
        with AI-generated answers via Groq.
        """
        textareas = await page.query_selector_all(
            "textarea"
        )
        for ta in textareas:
            question = await self._get_label(page, ta)
            if not question:
                continue

            # Skip if already filled
            existing = await ta.evaluate(
                "el => el.value"
            )
            if existing and len(existing) > 10:
                continue

            answer = await self._ai_answer(
                question, user, job
            )
            if answer:
                await ta.fill(answer)
                await asyncio.sleep(0.3)

        # Also handle select dropdowns for common fields
        selects = await page.query_selector_all("select")
        for sel in selects:
            label = await self._get_label(page, sel)
            if not label:
                continue
            label_lower = label.lower()

            # Handle common yes/no questions
            if any(w in label_lower for w in [
                "authorized", "sponsorship",
                "legally", "eligible"
            ]):
                try:
                    await sel.select_option(
                        value="Yes",
                        timeout=2000
                    )
                except Exception:
                    pass

    async def _get_label(self, page: Page, el) -> str:
        """Finds the label text for a form element."""
        try:
            el_id = await el.get_attribute("id")
            if el_id:
                label = await page.query_selector(
                    f"label[for='{el_id}']"
                )
                if label:
                    return (
                        await label.inner_text()
                    ).strip()

            # Try aria-label
            aria = await el.get_attribute("aria-label")
            if aria:
                return aria.strip()

            # Try placeholder
            ph = await el.get_attribute("placeholder")
            if ph:
                return ph.strip()

        except Exception:
            pass
        return ""

    async def _ai_answer(
        self, question: str, user: dict, job: dict
    ) -> str:
        try:
            return await chat_complete(
                system=(
                    "You are filling out a job application. "
                    "Write concise professional answers. "
                    "Max 3 sentences. No buzzwords."
                ),
                user=(
                    f"Job: {job.get('title')} "
                    f"at {job.get('company')}\n"
                    f"About me: {user.get('summary', '')}\n"
                    f"Question: {question}\n"
                    f"Answer:"
                ),
                max_tokens=150
            )
        except Exception:
            return ""

    async def _submit(self, page: Page) -> bool:
        """Tries multiple submit button selectors."""
        selectors = [
            "#submit_app",
            "button[type='submit']",
            "input[type='submit']",
            "[data-qa='btn-submit']",
            "button:has-text('Submit')",
            "button:has-text('Apply')",
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
