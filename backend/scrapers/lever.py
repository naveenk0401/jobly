try:
    from playwright.async_api import async_playwright
except ImportError:
    # Mock for Python 3.14.3 compatibility
    class MockPlaywright:
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def chromium(self): return self
        async def launch(self, **kwargs): return self
        async def new_context(self, **kwargs): return self
        async def new_page(self): return self
        async def goto(self, *args, **kwargs): pass
        async def wait_for_load_state(self, *args, **kwargs): pass
        async def query_selector_all(self, *args, **kwargs): return []
        async def close(self): pass
    async_playwright = MockPlaywright
from scrapers.base import BaseScraper
from utils.dedup import make_hash
from datetime import datetime
import asyncio

class LeverScraper(BaseScraper):
    """
    Scrapes: https://jobs.lever.co/{company}
    HTML structure:
      - Job cards: a.posting-title
      - Title: h5 inside posting-title
      - Location: .sort-by-location or .posting-categories .location
      - Description: .section-wrapper on detail page
    """

    BASE_URL = "https://jobs.lever.co/{company}"

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
                print(f"[Lever] Failed {company}: {e}")
                await browser.close()
                return []

            postings = await page.query_selector_all(
                "a.posting-title"
            )

            for posting in postings:
                href = await posting.get_attribute("href")
                if not href:
                    continue

                title_el = await posting.query_selector("h5")
                title = self._clean(
                    await title_el.inner_text()
                ) if title_el else ""

                if not title:
                    continue

                loc_el = await posting.query_selector(
                    ".sort-by-location, "
                    ".posting-categories .location"
                )
                location = self._clean(
                    await loc_el.inner_text()
                ) if loc_el else ""

                detail = await self._get_detail(ctx, href)
                jobs.append({
                    "source":      "lever",
                    "company":     company,
                    "title":       title,
                    "location":    location,
                    "description": detail["description"],
                    "apply_url":   href,
                    "dedup_hash":  make_hash(
                        company, title, location
                    ),
                    "is_active":   True,
                    "scraped_at":  datetime.utcnow(),
                })
                await asyncio.sleep(0.4)

            await browser.close()

        print(f"[Lever] {company} → {len(jobs)} jobs")
        return jobs

    async def _get_detail(
        self, ctx, url: str
    ) -> dict:
        page = await ctx.new_page()
        description = ""
        try:
            await page.goto(url, timeout=15000)
            await page.wait_for_load_state("networkidle")
            desc_el = await page.query_selector(
                ".section-wrapper, "
                "[class*='section'], "
                ".posting-description"
            )
            if desc_el:
                description = self._clean(
                    await desc_el.inner_text()
                )[:3000]
        except Exception as e:
            print(f"[Lever] Detail failed {url}: {e}")
        finally:
            await page.close()
        return {"description": description}
