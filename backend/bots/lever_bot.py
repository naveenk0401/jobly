from playwright.async_api import async_playwright, Page
from utils.groq_client import chat_complete
import asyncio

class LeverBot:
    """
    Applies to jobs on jobs.lever.co

    Lever apply URL = job_url + "/apply"
    Form structure:
      - name:   input[name='name']
      - email:  input[name='email']
      - phone:  input[name='phone']
      - org:    input[name='org'] (current company)
      - resume: input[type='file']
      - custom: textarea elements with labels
      - submit: button[type='submit'],
                .application-submit
    """

    async def apply(
        self,
        job: dict,
        user: dict,
        resume_path: str
    ) -> dict:
        # Build apply URL
        apply_url = job["apply_url"]
        if not apply_url.endswith("/apply"):
            apply_url = apply_url.rstrip("/") + "/apply"

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
                    apply_url, timeout=20000
                )
                await page.wait_for_load_state("networkidle")

                # Wait for the form
                await page.wait_for_selector(
                    "input[name='name'], "
                    "input[name='email']",
                    timeout=8000
                )

                # Fill standard fields
                await self._fill(
                    page, "input[name='name']",
                    user.get("name", "")
                )
                await self._fill(
                    page, "input[name='email']",
                    user.get("email", "")
                )
                await self._fill(
                    page, "input[name='phone']",
                    user.get("phone", "")
                )
                # Current company (optional field)
                await self._fill(
                    page, "input[name='org']",
                    "Seeking New Opportunity"
                )

                # Resume upload
                upload = await page.query_selector(
                    "input[type='file']"
                )
                if upload:
                    await upload.set_input_files(resume_path)
                    await asyncio.sleep(1.5)

                # Custom questions
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
        textareas = await page.query_selector_all(
            "textarea"
        )
        for ta in textareas:
            try:
                ta_id = await ta.get_attribute("id")
                question = ""
                if ta_id:
                    label = await page.query_selector(
                        f"label[for='{ta_id}']"
                    )
                    if label:
                        question = (
                            await label.inner_text()
                        ).strip()

                if not question:
                    question = await ta.get_attribute(
                        "placeholder"
                    ) or ""

                if question:
                    answer = await chat_complete(
                        system=(
                            "You are applying for a job. "
                            "Be concise and professional. "
                            "Max 3 sentences."
                        ),
                        user=(
                            f"Job: {job.get('title')} "
                            f"at {job.get('company')}\n"
                            f"Background: "
                            f"{user.get('summary', '')}\n"
                            f"Question: {question}"
                        ),
                        max_tokens=150
                    )
                    if answer:
                        await ta.fill(answer)
                        await asyncio.sleep(0.3)
            except Exception:
                continue

    async def _submit(self, page: Page) -> bool:
        selectors = [
            "button[type='submit']",
            ".application-submit button",
            "button:has-text('Submit application')",
            "button:has-text('Submit')",
            "input[type='submit']",
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
