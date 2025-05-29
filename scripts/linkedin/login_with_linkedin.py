# pylint: disable=broad-exception-caught

import os
from playwright.async_api import Page
from utils.handle_exceptions import handle_exceptions


@handle_exceptions(raise_on_error=True)
async def login_linkedin(page: Page):
    await page.goto("https://www.linkedin.com/login")
    await page.wait_for_load_state("networkidle")

    # username is sometimes already set and doesn't exist
    try:
        username = os.getenv("LINKEDIN_USERNAME", "")
        await page.fill('input[id="username"]', username, timeout=1000)
    except Exception:
        print("Username input not found, continuing...")

    # Process password input
    await page.fill('input[id="password"]', os.getenv("LINKEDIN_PASSWORD", ""))
    await page.click('button[type="submit"]')
    await page.wait_for_load_state("domcontentloaded")
