import json
import os
from playwright.async_api import BrowserContext
from utils.handle_exceptions import handle_exceptions


@handle_exceptions(default_return_value=None, raise_on_error=False)
async def save_auth_state(context: BrowserContext):
    auth_file = os.path.join(os.path.expanduser("~"), "Downloads", "linkedin-auth.json")
    storage_state = await context.storage_state()
    with open(auth_file, "w", encoding="utf-8") as f:
        json.dump(storage_state, f)
    print(f"Saved new auth state to {auth_file}")
