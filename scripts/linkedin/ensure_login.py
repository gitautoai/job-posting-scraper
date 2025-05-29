# pylint: disable=broad-exception-caught

from playwright.async_api import Page
from scripts.linkedin.login_with_linkedin import login_linkedin
from scripts.linkedin.save_auth_state import save_auth_state
from utils.handle_exceptions import handle_exceptions


@handle_exceptions(raise_on_error=True)
async def ensure_linkedin_login(page: Page):
    try:
        text = "Sign in to view more jobs"
        signin_popup = await page.wait_for_selector(f"text={text}", timeout=5000)
        if signin_popup is not None:
            print("Not logged in, performing login...")
            await login_linkedin(page)
            await save_auth_state(page.context)
    except Exception:
        # No sign-in popup found, assuming already logged in
        return
