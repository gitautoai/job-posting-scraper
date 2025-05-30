# pylint: disable=broad-exception-caught
# pylint: disable=line-too-long
# noqa: E501

# Standard imports
import asyncio
import json
import os
import sys
from typing import Any
from urllib.parse import quote

# Third party imports
from playwright.async_api import async_playwright

# Local imports
from scripts.google.get_google_sheets_service import get_google_sheets_service
from scripts.google.read_from_sheets import read_from_sheets
from scripts.google.write_to_sheets import write_to_sheets
from scripts.linkedin.ensure_login import ensure_linkedin_login
from scripts.linkedin.login_with_linkedin import login_linkedin
from scripts.linkedin.search_jobs import search_linkedin_jobs
from scripts.slack.slack import slack


async def main():
    # Get the keyword from command line arguments or environment variable
    keyword = os.getenv("SEARCH_KEYWORD", "Test Automation Engineer")
    if len(sys.argv) > 1:
        keyword = sys.argv[1]

    print(f"Using search keyword: {keyword}")

    async with async_playwright() as p:
        # Launch browser in headless mode based on environment
        env = os.getenv("ENV", "")
        is_local = env.lower() == "local"

        # Always run headless in GitHub Actions
        browser = await p.chromium.launch(headless=not is_local)
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"  # noqa: E501

        context_options: dict[str, Any] = {}

        # For local development, use local auth file
        if is_local:
            auth_file = os.path.join(
                os.path.expanduser("~"), "Downloads", "linkedin-auth.json"
            )
            if os.path.exists(auth_file):
                print(f"Loading storage state from {auth_file}")
                with open(auth_file, "r", encoding="utf-8") as f:
                    storage_state = json.load(f)
                    context_options["storage_state"] = storage_state

        # For GitHub Actions, use LINKEDIN_AUTH_JSON environment variable
        else:
            linkedin_auth_json = os.getenv("LINKEDIN_AUTH_JSON")
            if linkedin_auth_json:
                try:
                    storage_state = json.loads(linkedin_auth_json)
                    print(
                        "Loaded LinkedIn auth from LINKEDIN_AUTH_JSON environment variable"
                    )
                    context_options["storage_state"] = storage_state
                except Exception as e:
                    print(f"Failed to parse LINKEDIN_AUTH_JSON: {e}")

        context = await browser.new_context(user_agent=user_agent, **context_options)
        page = await context.new_page()

        try:
            if not context_options:
                print("No auth state found, performing login...")
                await login_linkedin(page)

            # Ensure logged in before searching
            await ensure_linkedin_login(page)

            # Get Google Sheets service
            sheets_service = get_google_sheets_service()

            # Use SPREADSHEET_ID from environment if available, otherwise fail
            spreadsheet_id = os.getenv("SPREADSHEET_ID")
            if not spreadsheet_id:
                raise ValueError("SPREADSHEET_ID environment variable is required")

            # Encode keyword for URL
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

            print(f"\nFetching page 1 for keyword: {keyword}")
            await page.goto(url)
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(2000)

            # Get jobs from first page
            jobs = await search_linkedin_jobs(page, keyword)
            print(f"Found {len(jobs)} jobs on page 1")
            new_jobs_count = write_to_sheets(sheets_service, spreadsheet_id, jobs)
            total_new_jobs = new_jobs_count

            # Only fetch additional pages when running locally
            if is_local:
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
                    new_jobs_count = write_to_sheets(
                        sheets_service, spreadsheet_id, jobs
                    )
                    total_new_jobs += new_jobs_count

            # Get total jobs count
            existing_jobs = read_from_sheets(sheets_service, spreadsheet_id)
            total_jobs = len(existing_jobs)

            # Send Slack notification
            slack(
                f"Job Search Results for '{keyword}':\n"
                f"• New jobs added: {total_new_jobs}\n"
                f"• Total jobs in database: {total_jobs}"
            )

        finally:
            await browser.close()


if __name__ == "__main__":
    # Run the script with: python -m main [keyword]
    asyncio.run(main())
