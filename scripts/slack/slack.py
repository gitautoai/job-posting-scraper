# Standard imports
import os

# Third party imports
import requests

# Local imports
from utils.handle_exceptions import handle_exceptions

URL = os.getenv("SLACK_WEBHOOK_URL")


@handle_exceptions(default_return_value=None, raise_on_error=False)
def slack(text: str):
    if not URL:
        return None
    requests.post(URL, json={"text": text}, timeout=20)
    return None
