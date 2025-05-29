# pylint: disable=broad-exception-caught
# pylint: disable=line-too-long
# noqa: E501

# Standard imports
import asyncio
import json
import os
from typing import Any
from urllib.parse import quote

# Third party imports
from playwright.async_api import async_playwright

# Local imports
from scripts.google import get_google_sheets_service, write_to_sheets
from scripts.linkedin.ensure_login import ensure_linkedin_login
from scripts.linkedin.login_with_linkedin import login_linkedin
from scripts.linkedin.search_jobs import search_linkedin_jobs


async def main():
    async with async_playwright() as p:
        # Launch browser in headless mode based on environment
        env = os.getenv("ENV", "")
        is_local = env.lower() == "local"

        browser = await p.chromium.launch(headless=not is_local)
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"  # noqa: E501

        auth_file = os.path.join(
            os.path.expanduser("~"), "Downloads", "linkedin-auth.json"
        )
        context_options: dict[str, Any] = {}

        if os.path.exists(auth_file):
            print(f"Loading storage state from {auth_file}")
            with open(auth_file, "r", encoding="utf-8") as f:
                storage_state = json.load(f)
                context_options["storage_state"] = storage_state

        context = await browser.new_context(user_agent=user_agent, **context_options)
        page = await context.new_page()

        try:
            if not context_options:
                print("Logging in to LinkedIn")
                await login_linkedin(page)

            # Ensure logged in before searching
            await ensure_linkedin_login(page)

            # Get Google Sheets service
            sheets_service = get_google_sheets_service()
            spreadsheet_id = "1acuQFPRf1cLDTDOeXpvlawxpk-G2KB48H8XBUOqv6AI"

            # Read first page
            keyword = "Test Automation Engineer"
            encoded_keyword = quote(keyword)

            # Build the search URL with filters
            base_url = "https://www.linkedin.com/jobs/search/"
            filters = {
                # Job titles filter
                "f_T": quote("11227,13936,4729,264,661,20648,1510"),
                "geoId": "103644278",  # United States
                "keywords": encoded_keyword,
            }

            # Construct URL with parameters
            url_params = "&".join([f"{k}={v}" for k, v in filters.items()])
            url = f"{base_url}?{url_params}"

            print("Fetching page 1")
            await page.goto(url)
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(2000)

            # Get jobs from first page
            jobs = await search_linkedin_jobs(page, keyword)
            print(f"Found {len(jobs)} jobs on page 1")
            write_to_sheets(sheets_service, spreadsheet_id, jobs)

            # Get jobs from pages 2 to 4
            for page_num in range(2, 5):
                print(f"Fetching page {page_num}")

                # Click pagination button
                next_page_button = f'button[aria-label="Page {page_num}"]'
                await page.wait_for_selector(next_page_button)
                await page.click(next_page_button)
                await page.wait_for_load_state("domcontentloaded")
                await page.wait_for_timeout(3000)  # Wait for page transition

                # Get jobs
                jobs = await search_linkedin_jobs(page, keyword)
                print(f"Found {len(jobs)} jobs on page {page_num}")
                write_to_sheets(sheets_service, spreadsheet_id, jobs)

        finally:
            await browser.close()


if __name__ == "__main__":
    # Run the script with: python -m main.py
    asyncio.run(main())
