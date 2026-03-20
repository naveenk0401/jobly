from playwright.async_api import async_playwright
from scrapers.base import BaseScraper
from utils.dedup import make_hash
from datetime import datetime
import asyncio

class GreenhouseScraper(BaseScraper):
    """
    Scrapes: https://boards.greenhouse.io/{company}
    HTML structure:
      - Job links: <a href="/company/jobs/123">Title</a>
      - Location: .location class on detail page
      - Description: #content div on detail page
    """

    BASE_URL = "https://boards.greenhouse.io/{company}"

    async def scrape(self, company: str) -> list[dict]:
        jobs = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            ctx     = await browser.new_context(
                user_agent="Mozilla/5.0 (compatible; Jobly/1.0)"
            )
            page = await ctx.new_page()

            try:
                url = self.BASE_URL.format(company=company)
                await page.goto(url, timeout=20000)
                await page.wait_for_load_state("networkidle")
            except Exception as e:
                print(f"[Greenhouse] Failed {company}: {e}")
                await browser.close()
                return []

            # Collect all job links from listing page
            links = await page.query_selector_all(
                "a[href*='/jobs/']"
            )
            seen = set()

            for link in links:
                href  = await link.get_attribute("href")
                title = self._clean(await link.inner_text())

                if not href or not title or href in seen:
                    continue
                if len(title) < 3 or len(title) > 200:
                    continue
                seen.add(href)

                apply_url = (
                    f"https://boards.greenhouse.io{href}"
                    if href.startswith("/") else href
                )

                detail = await self._get_detail(ctx, apply_url)
                jobs.append({
                    "source":      "greenhouse",
                    "company":     company,
                    "title":       title,
                    "location":    detail["location"],
                    "description": detail["description"],
                    "apply_url":   apply_url,
                    "dedup_hash":  make_hash(
                        company, title, detail["location"]
                    ),
                    "is_active":   True,
                    "scraped_at":  datetime.utcnow(),
                })
                await asyncio.sleep(0.4)

            await browser.close()

        print(f"[Greenhouse] {company} → {len(jobs)} jobs")
        return jobs

    async def _get_detail(
        self, ctx, url: str
    ) -> dict:
        page = await ctx.new_page()
        location    = ""
        description = ""
        try:
            await page.goto(url, timeout=15000)
            await page.wait_for_load_state("networkidle")

            loc_el = await page.query_selector(".location")
            if loc_el:
                location = self._clean(
                    await loc_el.inner_text()
                )

            desc_el = await page.query_selector(
                "#content, .content, [class*='content']"
            )
            if desc_el:
                description = self._clean(
                    await desc_el.inner_text()
                )[:3000]

        except Exception as e:
            print(f"[Greenhouse] Detail failed {url}: {e}")
        finally:
            await page.close()

        return {"location": location, "description": description}
