from abc import ABC, abstractmethod

class BaseScraper(ABC):

    @abstractmethod
    async def scrape(self, company: str) -> list[dict]:
        """
        Scrape all jobs for a given company slug.
        Returns list of job dicts, each containing:
          source, company, title, location,
          description, apply_url, dedup_hash,
          is_active, scraped_at
        """
        pass

    def _clean(self, text: str) -> str:
        """Strip whitespace and normalize."""
        return " ".join(text.split()) if text else ""
