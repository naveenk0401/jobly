import asyncio
from playwright.async_api import async_playwright

async def main():
    """
    Opens a Greenhouse apply page visually
    so you can watch what the bot sees.
    Headless=False — a browser window will open.
    """
    print("Opening browser visually...")
    print("Watch what the bot sees.")
    print("Press Ctrl+C to stop.\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=500   # slows actions by 500ms
        )
        page = await browser.new_page()

        # Use a real Greenhouse apply page
        test_url = (
            "https://boards.greenhouse.io/stripe/jobs/"
            "5000000"   # replace with a real job ID
        )

        print(f"Navigating to: {test_url}")
        await page.goto(test_url, timeout=20000)
        await page.wait_for_load_state("networkidle")

        print(f"Page title: {await page.title()}")

        # List all inputs found
        inputs = await page.query_selector_all("input")
        print(f"\nFound {len(inputs)} input fields:")
        for inp in inputs:
            name = await inp.get_attribute("name") or ""
            type_ = await inp.get_attribute("type") or "text"
            print(f"  [{type_}] name={name}")

        # List all textareas
        textareas = await page.query_selector_all("textarea")
        print(f"\nFound {len(textareas)} textareas")

        # Keep browser open for 10s
        await asyncio.sleep(10)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
