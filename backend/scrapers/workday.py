from playwright.async_api import async_playwright
from scrapers.base import BaseScraper
from utils.dedup import make_hash
from datetime import datetime
import asyncio

class WorkdayScraper(BaseScraper):
    """
    Workday URLs vary by company. Pass company as:
      "tenant|board|subdomain"
      e.g. "apple|apple|apple" 
           → apple.wd5.myworkday.com/apple/jobs

    Workday is heavily JS-rendered.
    Wait for job list selector before scraping.
    """

    async def scrape(self, company: str) -> list[dict]:
        parts  = company.split("|")
        tenant = parts[0]
        board  = parts[1] if len(parts) > 1 else tenant
        sub    = parts[2] if len(parts) > 2 else tenant

        url = f"https://{sub}.wd5.myworkday.com/{board}/jobs"
        jobs = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            ctx     = await browser.new_context(
                user_agent="Mozilla/5.0 (compatible; Jobly/1.0)"
            )
            page = await ctx.new_page()

            try:
                await page.goto(url, timeout=30000)
                await page.wait_for_load_state("networkidle")
                # Workday is slow — wait for job cards
                await page.wait_for_selector(
                    "[data-automation-id='compositeContainer'],"
                    "li.css-1q2dra3,"
                    "[data-automation-id='jobTitle']",
                    timeout=20000
                )
            except Exception as e:
                print(f"[Workday] Failed {company}: {e}")
                await browser.close()
                return []

            # Try multiple known Workday job card selectors
            selectors = [
                "[data-automation-id='compositeContainer']",
                "li.css-1q2dra3",
                "li[class*='css-']"
            ]

            items = []
            for sel in selectors:
                items = await page.query_selector_all(sel)
                if items:
                    break

            for item in items:
                title_el = await item.query_selector(
                    "[data-automation-id='jobTitle'],"
                    "h3 a, .css-19uc56f, a[href*='/job/']"
                )
                if not title_el:
                    continue

                title = self._clean(
                    await title_el.inner_text()
                )
                href = await title_el.get_attribute("href")

                if not title or not href:
                    continue

                apply_url = (
                    href if href.startswith("http")
                    else f"https://{sub}.wd5.myworkday.com{href}"
                )

                loc_el = await item.query_selector(
                    "[data-automation-id='locations'],"
                    ".css-129m7dg, [class*='location']"
                )
                location = self._clean(
                    await loc_el.inner_text()
                ) if loc_el else ""

                jobs.append({
                    "source":      "workday",
                    "company":     tenant,
                    "title":       title,
                    "location":    location,
                    "description": "",
                    "apply_url":   apply_url,
                    "dedup_hash":  make_hash(
                        tenant, title, location
                    ),
                    "is_active":   True,
                    "scraped_at":  datetime.utcnow(),
                })
                await asyncio.sleep(0.3)

            await browser.close()

        print(f"[Workday] {company} → {len(jobs)} jobs")
        return jobs
